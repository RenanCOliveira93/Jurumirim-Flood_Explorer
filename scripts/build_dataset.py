#!/usr/bin/env python
"""Fases 0-2: extrai seções, georreferencia, vetoriza manchas e roda interseções."""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402
from shapely.geometry import Point  # noqa: E402

from jurumirim import gis  # noqa: E402
from jurumirim.georef import CRS, fit_transform, independent_check, section_lines  # noqa: E402
from jurumirim.pae import extract_sections  # noqa: E402
from jurumirim.paths import METADATA, PDF, PROCESSED  # noqa: E402
from jurumirim.vectorize import vectorize  # noqa: E402

PROCESSED.mkdir(parents=True, exist_ok=True)
METADATA.mkdir(parents=True, exist_ok=True)


def main():
    sec = extract_sections()
    sec.to_csv(PROCESSED / "pae_sections.csv", index=False)
    pts = gpd.GeoDataFrame(sec, geometry=[Point(x, y) for x, y in zip(sec.x_utm, sec.y_utm)], crs=CRS)

    A, ginfo = fit_transform()
    chk = independent_check(A, sec, section_lines())
    ginfo["checagem_independente_m"] = {k: round(v, 2) for k, v in chk.items()}
    ginfo["checagem_independente_nota"] = (
        "distância do ponto central tabelado ao traço de seção mais próximo na prancha; "
        "ST-001 (seção da brecha) não tem traço próprio equivalente na prancha.")

    gdf, q, _ = vectorize()
    env = gdf[gdf.classe == "ENVOLTORIA_RUPTURA"].geometry.iloc[0]
    # cheia sem ruptura: recorta ruído (reservatório/hidrografia) fora da envoltória
    m = gdf.classe == "CHEIA_SR"
    gdf.loc[m, "geometry"] = gdf.loc[m].geometry.intersection(env.buffer(40))
    gdf = gdf[~gdf.geometry.is_empty].copy()
    gdf["area_km2"] = gdf.geometry.area / 1e6
    gdf["valido"] = gdf.geometry.is_valid
    gdf["confianca"] = gdf.classe.map({
        "ZAS": "média", "ZSS": "média", "ENVOLTORIA_RUPTURA": "média", "ZSS_APENAS": "média",
        "CHEIA_SR": "baixa (linha azul alterada pelo tom ZAS e sobreposta ao reservatório; recortada)"})
    gpkg = PROCESSED / "pae_flood_polygons.gpkg"
    gpkg.unlink(missing_ok=True)
    gdf.to_file(gpkg, layer="manchas", driver="GPKG")
    pts.to_file(gpkg, layer="secoes", driver="GPKG")
    gdf.to_crs(4326).to_file(PROCESSED / "pae_flood_polygons.geojson", driver="GeoJSON")
    pts.to_crs(4326).to_file(PROCESSED / "pae_sections.geojson", driver="GeoJSON")

    mun = gis.load_municipios()
    urb = gis.load_urbanizadas()
    roads = gis.load_roads()
    mo = gis.municipality_overlap(env, mun)
    uo = gis.urban_overlap(env, urb, mun)
    rc = gis.road_crossings(env, roads)
    mo.to_csv(PROCESSED / "overlap_municipios.csv", index=False)
    uo.to_csv(PROCESSED / "overlap_urbanizadas.csv", index=False)
    rc.to_csv(PROCESSED / "overlap_vias.csv", index=False)
    mun[mun.nome.isin(mo.municipio)].to_file(PROCESSED / "municipios_regiao.gpkg", driver="GPKG")

    prov = {
        "gerado_em": date.today().isoformat(),
        "fonte_primaria": {
            "documento": "CTG Brasil, PAE Externo UHE Jurumirim, CTG-SB-PAEE-2026-R0-JUR, jan/2026",
            "arquivo": PDF.name, "prancha": "CTG-SB-DE-2415-JUR (01/01), data 01/10/2024, escala 1:30.000 (ISO A1)",
            "pagina_fisica_pdf": 38, "crs_prancha": "SIRGAS 2000 / UTM 22S (EPSG:31982)",
            "cenario": "Ruptura isolada em dia seco, N.A. 568,00 m; cheia de projeto TR=10.000 anos sem ruptura",
        },
        "tipo_prancha": "mapa raster (basemap + contornos rasterizados) com tabela de seções em texto vetorial",
        "georreferenciamento": ginfo,
        "vetorizacao": {"metodo": "segmentação HSV das cores exatas da legenda + esqueleto + ligação de pontas "
                        "+ preenchimento; simplificação 2,5 m", "zoom_render": 3,
                        "resolucao_m_px": q["ZSS"]["m_por_pixel"], "qualidade_por_classe": q,
                        "limitacoes": [
                            "Raster -> vetor: posição das linhas tem incerteza de ~1-3 px (3,5-10 m) além da incerteza do próprio PAE.",
                            "Rótulos/ícones sobrepostos interrompem linhas; lacunas foram ligadas automaticamente (pontas restantes registradas).",
                            "CHEIA_SR tem baixa confiança; use apenas como indicativo.",
                            "Tabela de seções sobrepõe parte da prancha (canto superior direito) e foi excluída da vetorização.",
                        ]},
        "tabela_secoes": {"pagina_pdf": 38, "n_secoes": int(len(sec)),
                          "dupla_checagem": "texto vetorial do PDF comparado visualmente com a prancha renderizada; "
                                            "valores conferem. Erro ortográfico 'Propriedas MD' (ST-012) mantido da fonte.",
                          "unidades": {"distancia": "km", "sobrelevacao": "m", "velocidade": "m/s",
                                       "tempo": "hh:mm (sobrelevação de 0,61 m)", "vazao": "m3/s",
                                       "coordenadas": "UTM 22S, m"}},
        "pendencias": ["ST-017 sem vazão de pico na fonte ('-')."],
    }
    (METADATA / "pae_provenance.json").write_text(json.dumps(prov, ensure_ascii=False, indent=2))
    pd.set_option("display.width", 200)
    print(gdf.groupby("classe").area_km2.sum())
    print(mo.to_string()); print(uo.head(8).to_string()); print(rc.head(10).to_string())


if __name__ == "__main__":
    main()
