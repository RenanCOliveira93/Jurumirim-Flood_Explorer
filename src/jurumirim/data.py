"""Acesso aos dados processados (usado por app, notebooks e exportações)."""
from __future__ import annotations

import json
from functools import lru_cache

import geopandas as gpd
import pandas as pd

from . import gis
from .paths import METADATA, PROCESSED

LABELS = {  # etiquetas persistentes (docs/CONCEITO_E_PLANO.md)
    "OFICIAL": "DADO OFICIAL",
    "DERIVADO": "DERIVADO DO PAE",
    "ESTIMATIVA": "ESTIMATIVA EXPLORATÓRIA",
    "ILUSTRACAO": "ILUSTRAÇÃO",
}
SRC_TABLE = "PAE UHE Jurumirim (CTG-SB-PAEE-2026-R0-JUR), prancha CTG-SB-DE-2415-JUR, PDF p. 38"
PAGE_REFS = {
    "caracteristicas": "PDF p. 21", "estudo": "PDF p. 37", "prancha": "PDF p. 38",
    "vale": "PDF p. 52", "tempo": "PDF p. 54", "fig12": "PDF p. 55",
}


@lru_cache
def sections() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "pae_sections.csv")


@lru_cache
def polygons() -> gpd.GeoDataFrame:
    return gpd.read_file(PROCESSED / "pae_flood_polygons.gpkg", layer="manchas")


@lru_cache
def section_points() -> gpd.GeoDataFrame:
    return gpd.read_file(PROCESSED / "pae_flood_polygons.gpkg", layer="secoes")


@lru_cache
def provenance() -> dict:
    return json.loads((METADATA / "pae_provenance.json").read_text())


@lru_cache
def sources() -> dict:
    return json.loads((METADATA / "public_data_sources.json").read_text())


@lru_cache
def municipios() -> gpd.GeoDataFrame:
    return gis.load_municipios()


@lru_cache
def urbanizadas() -> gpd.GeoDataFrame:
    return gis.load_urbanizadas()


@lru_cache
def roads() -> gpd.GeoDataFrame:
    return gis.load_roads()


def envelope():
    p = polygons()
    return p[p.classe == "ENVOLTORIA_RUPTURA"].geometry.iloc[0]


def overlap_tables():
    return {k: pd.read_csv(PROCESSED / f"overlap_{k}.csv") for k in ("municipios", "urbanizadas", "vias")}


def urban_summary() -> dict:
    """Resumo data-driven da sobreposição com áreas urbanizadas IBGE 2019 no município de Piraju."""
    u = overlap_tables()["urbanizadas"]
    pir = u[u.municipio == "Piraju"].sort_values("area_km2", ascending=False)
    hit = pir[pir.area_na_envoltoria_km2 > 0]
    main = pir.iloc[0]
    return {
        "main_area_km2": float(main.area_km2),
        "main_distance_m": float(main.distancia_a_envoltoria_m),
        "main_intersects": bool(main.area_na_envoltoria_km2 > 0),
        "n_polygons_piraju": int(len(pir)),
        "n_intersecting": int(len(hit)),
        "intersecting_area_km2": float(hit.area_na_envoltoria_km2.sum()),
        "intersecting_polygons": hit[["id_poligono", "densidade", "area_km2", "area_na_envoltoria_km2",
                                      "pct_na_envoltoria"]].to_dict("records"),
        "nearest_other_m": float(pir[pir.area_na_envoltoria_km2 == 0].distancia_a_envoltoria_m.min()),
    }
