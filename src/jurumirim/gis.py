"""Integração SIG: limites IBGE, áreas urbanizadas, vias OSM e interseções em CRS projetado."""
from __future__ import annotations

import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

from .georef import CRS
from .paths import PROCESSED, RAW

PIRAJU_CODE = "3538808"  # código IBGE do município de Piraju (SP)


def load_municipios(crs=CRS) -> gpd.GeoDataFrame:
    g = gpd.read_file(RAW / "ibge_municipios_sp.geojson")
    names = json.loads((RAW / "ibge_municipios_sp_nomes.json").read_text())
    g["nome"] = g["codarea"].map(names)
    g = g.set_crs("EPSG:4674", allow_override=True) if g.crs is None else g
    return g.to_crs(crs)


def load_urbanizadas(crs=CRS) -> gpd.GeoDataFrame:
    return gpd.read_file(RAW / "ibge_areas_urbanizadas_2019_regiao.gpkg").to_crs(crs)


def load_roads(crs=CRS) -> gpd.GeoDataFrame:
    data = json.loads((RAW / "osm_roads.json").read_text())
    rows = []
    for e in data["elements"]:
        if e["type"] == "way" and len(e.get("geometry", [])) >= 2:
            t = e.get("tags", {})
            rows.append({"osm_id": e["id"], "highway": t.get("highway"), "ref": t.get("ref"),
                         "name": t.get("name"),
                         "geometry": LineString([(p["lon"], p["lat"]) for p in e["geometry"]])})
    return gpd.GeoDataFrame(rows, crs="EPSG:4326").to_crs(crs)


def municipality_overlap(envelope_geom, municipios: gpd.GeoDataFrame, crs_check=True) -> pd.DataFrame:
    assert municipios.crs.is_projected, "áreas só em CRS projetado"
    out = []
    for _, m in municipios.iterrows():
        inter = m.geometry.intersection(envelope_geom)
        if inter.area > 0:
            out.append({"municipio": m.nome, "codigo_ibge": m.codarea,
                        "area_municipio_km2": m.geometry.area / 1e6,
                        "area_envoltoria_no_municipio_km2": inter.area / 1e6,
                        "pct_do_municipio": 100 * inter.area / m.geometry.area})
    cols = ["municipio", "codigo_ibge", "area_municipio_km2",
            "area_envoltoria_no_municipio_km2", "pct_do_municipio"]
    return pd.DataFrame(out, columns=cols).sort_values("area_envoltoria_no_municipio_km2", ascending=False)


def urban_overlap(envelope_geom, urb: gpd.GeoDataFrame, municipios: gpd.GeoDataFrame) -> pd.DataFrame:
    """Para cada polígono urbanizado IBGE: município, área, área na envoltória, distância à envoltória."""
    assert urb.crs.is_projected
    rows = []
    for i, u in urb.iterrows():
        c = u.geometry.representative_point()
        mun = municipios[municipios.contains(c)]
        inter = u.geometry.intersection(envelope_geom)
        rows.append({
            "id_poligono": i, "tipo": u.get("Tipo"), "densidade": u.get("Densidade"),
            "municipio": mun.nome.iloc[0] if len(mun) else None,
            "area_km2": u.geometry.area / 1e6,
            "area_na_envoltoria_km2": inter.area / 1e6,
            "pct_na_envoltoria": 100 * inter.area / u.geometry.area,
            "distancia_a_envoltoria_m": 0.0 if inter.area > 0 else u.geometry.distance(envelope_geom),
        })
    return pd.DataFrame(rows).sort_values("area_km2", ascending=False)


def road_crossings(envelope_geom, roads: gpd.GeoDataFrame) -> pd.DataFrame:
    sel = roads[roads.intersects(envelope_geom)].copy()
    sel["comprimento_na_envoltoria_km"] = sel.geometry.intersection(envelope_geom).length / 1e3
    return (sel.groupby(["ref", "highway"], dropna=False)["comprimento_na_envoltoria_km"]
            .agg(["sum", "count"]).reset_index()
            .rename(columns={"sum": "comprimento_km", "count": "segmentos"})
            .sort_values("comprimento_km", ascending=False))
