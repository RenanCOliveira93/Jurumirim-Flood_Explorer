#!/usr/bin/env python
"""Baixa dados públicos (IBGE, Copernicus DEM GLO-30, OpenStreetMap) de forma reproduzível.

Registra fonte, data de download, licença e datum em data/metadata/public_data_sources.json.
Nenhuma credencial é necessária.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
RAW.mkdir(parents=True, exist_ok=True)
META.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "jurumirim-flood-explorer/0.1 (projeto independente)"}
BBOX = (-49.55, -23.35, -49.15, -23.00)  # lon_min, lat_min, lon_max, lat_max (WGS84)
TODAY = dt.date.today().isoformat()
sources = {}


def get(url, **kw):
    r = requests.get(url, headers=UA, timeout=180, **kw)
    r.raise_for_status()
    return r


def ibge():
    url = ("https://servicodados.ibge.gov.br/api/v3/malhas/estados/35"
           "?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=intermediaria")
    (RAW / "ibge_municipios_sp.geojson").write_bytes(get(url).content)
    names = get("https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios").json()
    (RAW / "ibge_municipios_sp_nomes.json").write_text(json.dumps(
        {str(n["id"]): n["nome"] for n in names}, ensure_ascii=False))
    sources["ibge_municipios"] = {
        "arquivo": "data/raw/ibge_municipios_sp.geojson", "url": url,
        "baixado_em": TODAY, "licenca": "Dados abertos IBGE (CC BY 4.0 / uso livre com citação)",
        "datum": "SIRGAS 2000 (EPSG:4674)", "qualidade_malha": "intermediária",
        "observacao": "Malha municipal digital IBGE via API v3; precisão cartográfica ~escala 1:250.000 — não é cadastral.",
    }


def ibge_urban():
    import tempfile, zipfile
    import geopandas as gpd
    url = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/tipologias_do_territorio/"
           "areas_urbanizadas_do_brasil/2019/Shapefile/AreasUrbanizadas2019_Brasil.zip")
    with tempfile.TemporaryDirectory() as td:
        z = Path(td) / "au.zip"
        with requests.get(url, headers=UA, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(z, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        out = Path(td) / "x"
        zipfile.ZipFile(z).extractall(out)
        shp = next(out.rglob("*.shp"))
        g = gpd.read_file(shp, bbox=BBOX)
        g.to_file(RAW / "ibge_areas_urbanizadas_2019_regiao.gpkg", driver="GPKG")
        crs = str(g.crs)
    sources["ibge_areas_urbanizadas_2019"] = {
        "arquivo": "data/raw/ibge_areas_urbanizadas_2019_regiao.gpkg", "url": url, "baixado_em": TODAY,
        "licenca": "Dados abertos IBGE (citar fonte)", "datum": crs,
        "observacao": "Áreas Urbanizadas do Brasil 2019 (mapeamento por imagens, ~1:100.000); delimita mancha urbanizada, NÃO o perímetro urbano legal.",
    }


def copernicus_dem():
    import rasterio
    from rasterio.windows import from_bounds
    tile = "Copernicus_DSM_COG_10_S24_00_W050_00_DEM"
    url = f"https://copernicus-dem-30m.s3.amazonaws.com/{tile}/{tile}.tif"
    with rasterio.open(url) as src:
        win = from_bounds(*BBOX, transform=src.transform)
        data = src.read(1, window=win)
        profile = src.profile.copy()
        profile.update(height=data.shape[0], width=data.shape[1], transform=src.window_transform(win),
                       driver="GTiff", compress="deflate", tiled=False)
        profile.pop("blockxsize", None); profile.pop("blockysize", None)
        out = RAW / "copernicus_glo30_jurumirim_piraju.tif"
        with rasterio.open(out, "w", **profile) as dst:
            dst.write(data, 1)
    sources["copernicus_glo30"] = {
        "arquivo": "data/raw/copernicus_glo30_jurumirim_piraju.tif", "url": url, "baixado_em": TODAY,
        "licenca": "Copernicus DEM GLO-30 — licença Copernicus (uso livre com atribuição: © DLR e.V. 2010-2014 / © Airbus DS 2014-2018 / produzido com dados Copernicus)",
        "resolucao": "1 arco-segundo (~30 m)", "tipo": "MDS (superfície, inclui vegetação/edificações)",
        "datum_horizontal": "WGS84 (EPSG:4326)", "datum_vertical": "EGM2008 (altitude ortométrica)",
        "precisao_vertical": "especificação: erro absoluto < 4 m (90%) em terreno plano; maior em relevo/vegetação",
        "bbox_wgs84": BBOX,
    }


OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OVERPASS = OVERPASS_MIRRORS[0]


def overpass(q):
    last = None
    for url in OVERPASS_MIRRORS:
        for _ in range(2):
            try:
                r = requests.post(url, data={"data": q}, headers=UA, timeout=240)
                r.raise_for_status()
                return r, url
            except Exception as ex:  # noqa: BLE001
                last = ex
    raise last



def osm():
    s, w, n, e = BBOX[1], BBOX[0], BBOX[3], BBOX[2]
    q_roads = f'[out:json][timeout:120];way["highway"~"motorway|trunk|primary|secondary|tertiary"]({s},{w},{n},{e});out geom;'
    q_urban = (f'[out:json][timeout:120];(way["landuse"~"residential|commercial|industrial|retail"]({s},{w},{n},{e});'
               f'relation["landuse"~"residential|commercial|industrial|retail"]({s},{w},{n},{e}););out geom;')
    for name, q in (("osm_roads", q_roads), ("osm_landuse_urban", q_urban)):
        r, used = overpass(q)
        print("   overpass:", used)
        (RAW / f"{name}.json").write_bytes(r.content)
    sources["openstreetmap"] = {
        "arquivos": ["data/raw/osm_roads.json", "data/raw/osm_landuse_urban.json"], "url": OVERPASS,
        "baixado_em": TODAY, "licenca": "ODbL 1.0 — © colaboradores do OpenStreetMap",
        "datum": "WGS84 (EPSG:4326)",
        "observacao": "landuse residencial/comercial/industrial usado como PROXY de área urbana (colaborativo, incompleto); não é o limite oficial de perímetro urbano.",
    }


def osm_waterways():
    """Eixo do rio Paranapanema (OSM) para posicionar, por quilometragem, as seções dos PAEs de Piraju/Paranapanema."""
    s, w, n, e = BBOX[1], BBOX[0], BBOX[3], BBOX[2]
    q = f'[out:json][timeout:120];way["waterway"~"river|canal"]({s},{w},{n},{e});out geom;'
    r, used = overpass(q)
    print("   overpass:", used)
    (RAW / "osm_waterways.json").write_bytes(r.content)
    sources["openstreetmap_waterways"] = {
        "arquivos": ["data/raw/osm_waterways.json"], "url": used, "baixado_em": TODAY,
        "licenca": "ODbL 1.0 — © colaboradores do OpenStreetMap", "datum": "WGS84 (EPSG:4326)",
        "observacao": "Eixo colaborativo do rio, usado só para posicionar seções por distância ao longo do rio (ILUSTRAÇÃO); não é o levantamento topobatimétrico do PAE.",
    }


def osm_water():
    """Corpos d'água atuais (reservatórios e calha do rio) para a camada 'situação normal' (comparação)."""
    s, w, n, e = BBOX[1], BBOX[0], BBOX[3], BBOX[2]
    q = (f'[out:json][timeout:180];(way["natural"="water"]({s},{w},{n},{e});relation["natural"="water"]({s},{w},{n},{e});'
         f'way["waterway"="riverbank"]({s},{w},{n},{e}););out geom;')
    r, used = overpass(q)
    print("   overpass:", used)
    (RAW / "osm_water.json").write_bytes(r.content)
    sources["openstreetmap_water"] = {
        "arquivos": ["data/raw/osm_water.json"], "url": used, "baixado_em": TODAY,
        "licenca": "ODbL 1.0 — © colaboradores do OpenStreetMap", "datum": "WGS84 (EPSG:4326)",
        "observacao": "Água em condição atual/normal (colaborativo; a data da imagem-base varia). Camada de COMPARAÇÃO, não é resultado de simulação.",
    }


if __name__ == "__main__":
    steps = {"ibge": ibge, "ibge_urban": ibge_urban, "dem": copernicus_dem, "osm": osm, "osm_waterways": osm_waterways, "osm_water": osm_water}
    chosen = sys.argv[1:] or list(steps)
    prev = json.loads((META / "public_data_sources.json").read_text()) if (META / "public_data_sources.json").exists() else {}
    for c in chosen:
        try:
            print("->", c); steps[c]()
        except Exception as ex:  # noqa: BLE001
            print(f"FALHOU {c}: {ex}", file=sys.stderr)
    prev.update(sources)
    (META / "public_data_sources.json").write_text(json.dumps(prev, ensure_ascii=False, indent=2))
    print("ok")
