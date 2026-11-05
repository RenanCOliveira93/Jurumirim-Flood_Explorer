#!/usr/bin/env python
"""Constrói, de forma INCREMENTAL, os dados das barragens a jusante (Piraju, Paranapanema).

Não toca nos arquivos de Jurumirim. Entradas: OCR bruto versionado (scripts/ocr_pae_images.py), OSM do eixo do rio
(scripts/fetch_public_data.py osm_waterways), PDFs (opcionais, só para checksums/figura). Saídas: data/processed/dams/.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pyproj import Transformer  # noqa: E402
from shapely.geometry import Point  # noqa: E402

from jurumirim import cascade, fig17, paths, piraju_tables as pt, riverpos  # noqa: E402
from jurumirim.dams_facts import FACTS  # noqa: E402

OUT = paths.PROCESSED / "dams"
RAWOCR = OUT / "PIR" / "ocr_raw"
TO_UTM = Transformer.from_crs(4674, 31982, always_xy=True)


def dms(d, m, s, hemi):
    v = d + m / 60 + s / 3600
    return -v if hemi in "SW" else v


def tables() -> dict:
    t = lambda n: pt.load(RAWOCR / n)  # noqa: E731
    a10 = pt.parse_table10(t("tabela10_top_s1.json"), t("tabela10_bottom_s1.json"))
    b10 = pt.parse_table10(t("tabela10_top_s1.5.json"), t("tabela10_bottom_s1.5.json"))
    a9, b9 = pt.parse_table9(t("tabela9_s2.json")), pt.parse_table9(t("tabela9_s3.json"))
    d10, d9 = pt.crosscheck(a10, b10), pt.crosscheck(a9, b9)
    meta = dict(source_document=cascade.DOC_PIR, extraction_method="OCR (rapidocr) das imagens embutidas, 2 escalas",
                verified=False)
    a10.assign(source_page="62 impressa / 63 PDF (Tabela 10)", **meta).to_csv(OUT / "PIR" / "sections_rupture.csv", index=False)
    a9.assign(source_page="61 impressa / 62 PDF (Tabela 9)", **meta).to_csv(OUT / "PIR" / "sections_natural.csv", index=False)
    return dict(tabela10_discordancias_ocr=d10, tabela9_discordancias_ocr=d9, n_rupture_rows=len(a10), n_natural_rows=len(a9))


def positions() -> dict:
    import cv2
    img = cv2.imread(str(RAWOCR / "fig17.png"))
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float)
    items = json.loads((RAWOCR / "fig17_s1.json").read_text())["items"]
    geo = fig17.georef(g, items)
    river = riverpos.river_line(paths.RAW / "osm_waterways.json")
    lat, lon = dms(23, 9, 19.13, "S"), dms(49, 22, 51.86, "W")  # PAE Piraju, Quadro 1 (p.13 impressa)
    plat, plon = dms(23, 11, 16, "S"), dms(49, 23, 4, "W")      # PAE Paranapanema, ficha técnica (p.5)
    pir, par = Point(*TO_UTM.transform(lon, lat)), Point(*TO_UTM.transform(plon, plat))
    sec = pd.read_csv(OUT / "PIR" / "sections_rupture.csv")
    sec = sec[sec.tr_anos == 10000].sort_values("secao")
    pl = riverpos.place(river, pir, sec.distancia_km.tolist())
    rows = []
    for (sid, d), (x, y) in zip(zip(sec.secao, sec.distancia_km), pl["points"]):
        lab = geo["labels"].get(sid)
        off = float(np.hypot(x - lab["x_utm"], y - lab["y_utm"])) if lab else None
        rows.append(dict(secao=sid, distancia_km=d, x_utm=round(x, 1), y_utm=round(y, 1), posicao="ilustrativa (km ao longo do eixo OSM)",
                         dist_ao_rotulo_fig17_m=None if off is None else round(off)))
    pd.DataFrame(rows).to_csv(OUT / "PIR" / "sections_positions.csv", index=False)
    s0 = river.project(pir)
    km_par = (river.project(par) - s0) / 1000
    p968 = river.interpolate(s0 + 9680)
    jur_st017 = Point(665709, 7438403)  # PAE Jurumirim, ST-017 'UHE Pirajú'
    pd.DataFrame([
        dict(dam="JUR", nome="UHE Jurumirim (seção da brecha ST-001)", x_utm=681083.0, y_utm=7432016.0, origem="PAE Jurumirim, tabela de seções (PDF p.38)"),
        dict(dam="PIR", nome="UHE Piraju", x_utm=round(pir.x, 1), y_utm=round(pir.y, 1), origem="PAE Piraju, Quadro 1 (p.13 impressa): 23°9'19,13\"S 49°22'51,86\"O"),
        dict(dam="PAR", nome="UHE Paranapanema", x_utm=round(par.x, 1), y_utm=round(par.y, 1), origem="PAE Paranapanema, ficha técnica (p.5): S 23°11'16\" W 49°23'04\""),
    ]).to_csv(OUT / "dams_positions.csv", index=False)
    rec = [r["dist_ao_rotulo_fig17_m"] for r in rows if r["dist_ao_rotulo_fig17_m"] is not None]
    return dict(
        fig17_rms_m=geo["rms_m"], fig17_max_residual_m=geo["max_residual_m"], fig17_n_control_points=geo["n_control_points"],
        fig17_pixel_size_m=geo["pixel_size_m"], fig17_labels_utm=geo["labels"], fig17_st08_fix=geo["st08_ocr_fix"],
        river_source="OSM waterway=river name='Rio Paranapanema' (ODbL), vias mescladas",
        piraju_dam_to_river_m=round(pl["origin_offset_m"]),
        km_osm_piraju_to_paranapanema_dam=round(float(km_par), 2), km_pae_piraju_zas=9.68,
        pos_9_68km_to_official_paranapanema_dam_m=round(float(p968.distance(par))),
        piraju_official_vs_jurumirim_st017_m=round(float(pir.distance(jur_st017))),
        label_offset_m_min=min(rec), label_offset_m_max=max(rec), label_offset_n=len(rec),
        nota="Posições das seções de Piraju por quilometragem sobre o eixo OSM: ILUSTRAÇÃO (±centenas de m). "
             "Distâncias a rótulos da Fig.17 só limitam grosseiramente (caixas de texto ficam ao lado das linhas).")


def facts_files():
    df = pd.DataFrame(FACTS)
    for dam, g in df.groupby("dam"):
        (OUT / dam).mkdir(parents=True, exist_ok=True)
        pub = g[~g.key.str.startswith("psb_")]
        pub.to_csv(OUT / dam / "facts.csv", index=False)
        if g.key.str.startswith("psb_").any():
            g[g.key.str.startswith("psb_")].to_csv(OUT / dam / "psb_facts.csv", index=False)  # gitignored


def main():
    (OUT / "PIR").mkdir(parents=True, exist_ok=True)
    report = dict(generated_on=str(date.today()))
    report.update(tables())
    report.update(positions())
    facts_files()
    (OUT / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    cascade.write_registry()
    print("ok:", {k: v for k, v in report.items() if not k.startswith("fig17_labels") and not isinstance(v, (list, dict))})
    print("discordâncias OCR T10/T9:", len(report["tabela10_discordancias_ocr"]), len(report["tabela9_discordancias_ocr"]))


if __name__ == "__main__":
    main()
