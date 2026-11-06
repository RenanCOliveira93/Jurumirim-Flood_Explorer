#!/usr/bin/env python
"""Gera os derivados de Piraju/Paranapanema: trechos de ZAS (oficiais, por extensão) e ESTIMATIVAS EXPLORATÓRIAS de mancha
(relevo preenchido até a cota máxima tabelada no PAE) com métricas de sobreposição e validação.

Tudo é DERIVADO/ESTIMATIVA: nada aqui é resultado hidráulico do PAE. Saídas em data/processed/dams/.
"""
import json
import sys
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from rasterio.features import rasterize
from scipy import ndimage as ndi
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jurumirim import bathtub as B, dams as D, fig17, gis, paths  # noqa: E402

OUT = paths.PROCESSED / "dams"
ZAS_KM = {"PIR": 9.68, "PAR": 10.0}   # PAE Piraju p.63 (impr.); PAE Paranapanema item 11 (p.18)
rows_mun, rows_urb, stats = [], [], {}

# 1) Trechos de ZAS (por extensão, como definidos nos PAEs)
for dam, km in ZAS_KM.items():
    line = B.zas_stretch(dam, km)
    gdf = gpd.GeoDataFrame([{"dam": dam, "zas_km_oficial": km, "comprimento_osm_km": round(line.length / 1000, 2),
                             "nota": "Trecho de rio com a extensão da ZAS definida no PAE; posição ILUSTRATIVA (eixo OSM)"}],
                           geometry=[line], crs=B.CRS)
    gdf.to_file(OUT / dam / "zas_trecho.gpkg", driver="GPKG")
    stats[f"zas_{dam}"] = dict(oficial_km=km, comprimento_osm_km=round(line.length / 1000, 2))

# 2) Estimativas (Piraju): ruptura (Tabela 10) e cheia natural (Tabela 9), TR 10 e 10.000
mun, urb = gis.load_municipios(), gis.load_urbanizadas()
feats = []
for kind in ("ruptura", "natural"):
    for tr in (10000, 10):
        poly, mask, aff_tr, kmcell = B.estimate(kind, tr)
        in_zas = mask & (kmcell <= ZAS_KM["PIR"])
        parts = {"ZAS": B.polygon_from_mask(in_zas, aff_tr), "alem_ZAS": B.polygon_from_mask(mask & ~in_zas, aff_tr)}
        key = f"{kind}_tr{tr}"
        stats[key] = dict(area_total_km2=round(poly.area / 1e6, 3), area_zas_km2=round(parts["ZAS"].area / 1e6, 3),
                          area_alem_zas_km2=round(parts["alem_ZAS"].area / 1e6, 3))
        for cl, g in parts.items():
            feats.append({"cenario": key, "tipo": kind, "tr_anos": tr, "classe": cl, "area_km2": g.area / 1e6, "geometry": g})
        for _, r in gis.municipality_overlap(poly, mun).iterrows():
            rows_mun.append({"cenario": key, **r.to_dict()})
        uo = gis.urban_overlap(poly, urb, mun)
        uo = uo[(uo.area_na_envoltoria_km2 > 0) | (uo.distancia_a_envoltoria_m < 2000)]
        for _, r in uo.iterrows():
            rows_urb.append({"cenario": key, **r.to_dict()})
        stats[key]["poligonos_urbanizados_intersectados"] = int((uo.area_na_envoltoria_km2 > 0).sum())
        stats[key]["area_urbanizada_intersectada_m2"] = round(float(uo.area_na_envoltoria_km2.sum()) * 1e6)
gpd.GeoDataFrame(feats, crs=B.CRS).to_file(OUT / "PIR" / "estimativa_mancha.gpkg", driver="GPKG")
pd.DataFrame(rows_mun).to_csv(OUT / "PIR" / "estimativa_overlap_municipios.csv", index=False)
pd.DataFrame(rows_urb).to_csv(OUT / "PIR" / "estimativa_overlap_urbanizadas.csv", index=False)

# 3) Validação: estimativa SEM ruptura × mancha clara da Figura 17 (também sem ruptura); só parte larga é segmentável
RAWOCR = OUT / "PIR" / "ocr_raw"
img = cv2.imread(str(RAWOCR / "fig17.png")); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
geo = fig17.georef(gray, json.loads((RAWOCR / "fig17_s1.json").read_text())["items"]); a = np.array(geo["affine"])
aff = Affine(a[0, 0], a[1, 0], a[2, 0], a[0, 1], a[1, 1], a[2, 1])
rgb = img[..., ::-1].astype(float); r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
m = (g_ - r_ >= 13) & (b_ - r_ >= 9) & (rgb.max(2) >= 118) & (g_ >= b_ - 6)
m[:12] = False; m[:, :12] = False; m[:, -12:] = False; m[640:] = False
m = ndi.binary_fill_holes(ndi.binary_closing(ndi.binary_opening(m, iterations=1), iterations=3))
lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = np.isin(lab, [i + 1 for i, s_ in enumerate(sz) if s_ > 800])
H, W = m.shape
box = np.zeros((H, W), bool); box[190:470, 690:920] = True  # reservatório a montante da barragem: fora da estimativa
m = m & ~box
poly, *_ = B.estimate("natural", 10000)
est = rasterize([(poly, 1)], out_shape=(H, W), transform=aff, fill=0, dtype="uint8").astype(bool); est[:10] = est[640:] = False
tol = ndi.binary_dilation(est, iterations=2)
stats["validacao_fig17_natural_tr10000"] = dict(
    cobertura_da_mancha_clara_sem_tolerancia=round(float((est & m).sum() / m.sum()), 3),
    cobertura_com_tolerancia_36m=round(float((tol & m).sum() / m.sum()), 3),
    nota=("Mede só quanto da parte LARGA e segmentável da mancha clara da Fig. 17 (cenário sem ruptura, sem legenda própria) "
          "a estimativa cobre. NÃO mede excesso: a segmentação perde o rio estreito. Georreferência da figura: RMS "
          f"{geo['rms_m']} m, {geo['pixel_size_m']} m/px."))
(OUT / "PIR" / "estimativa_metricas.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2))
print(json.dumps(stats, ensure_ascii=False, indent=1))
