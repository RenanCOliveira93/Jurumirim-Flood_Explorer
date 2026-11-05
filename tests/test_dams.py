import json

import numpy as np
import pandas as pd
import pytest

from jurumirim import dams as D
from jurumirim import fig17, paths, piraju_tables as pt, riverpos

OCR = paths.PROCESSED / "dams" / "PIR" / "ocr_raw"


def _item(text, x, y):
    return dict(text=text, x0=x, x1=x + 10, y0=y, y1=y + 10, conf=1)


def row10(sid, left, right, y):
    toks = [(f"ST-{sid:02d}", 0)] + [(t, 10 * (i + 1)) for i, t in enumerate(left)]
    toks += [(f"ST-{sid:02d}", 100)] + [(t, 100 + 10 * (i + 1)) for i, t in enumerate(right)]
    return [_item(t, x, y) for t, x in toks]


# ---------------------------------------------------------------- parser
def test_num_formats():
    assert pt.num("7,44") == 7.44 and pt.num("7.00") == 7.0 and pt.num("-") is None
    assert pt.num("26.857", flow=True) == 26857 and pt.num("2.834*", flow=True) == 2834
    with pytest.raises(ValueError):
        pt.num("abc")
    with pytest.raises(ValueError):
        pt.num("2834", flow=True)  # vazão sem separador de milhar: formato inesperado


def test_parse_table10_fails_loudly_on_wrong_field_count():
    ok = ["0,00", "501,71", "30,95", "7,44", "532,70", "26.857", "0", "0"]
    items = row10(0, ok, ok, 20)
    assert len(pt.parse_table10({"items": items}, {"items": []})) == 2
    with pytest.raises(ValueError):
        pt.parse_table10({"items": row10(0, ok[:-1], ok, 20)}, {"items": []})


def test_parse_table10_st22_missing_wave_time_is_nan():
    st22 = ["32,35", "441,73", "32,64", "3,19", "474,38", "2.834*", "165"]  # OCR descartou o '-' final
    df = pt.parse_table10({"items": row10(22, st22, st22, 20)}, {"items": []})
    assert df.t_frente_min.isna().all() and df.vazao_marcada_asterisco.all() and (df.vazao_max_m3s == 2834).all()


def test_crosscheck_reports_cell_differences():
    a = pd.DataFrame(dict(secao=["ST-01"], tr_anos=[10], x=[1.0]))
    b = pd.DataFrame(dict(secao=["ST-01"], tr_anos=[10], x=[1.1]))
    assert pt.crosscheck(a, a) == [] and pt.crosscheck(a, b)[0]["coluna"] == "x"


# ---------------------------------------------------------------- valores lidos direto da imagem (controle independente do OCR)
def test_piraju_spot_values_match_rendered_table_10():
    r = D.sections("PIR", "ruptura_tr10000").set_index("secao")
    assert (r.loc["ST-12", "t_frente_min"], r.loc["ST-12", "vazao_pico_m3s"], r.loc["ST-12", "vel_max_ms"]) == (19, 16467, 10.57)
    assert (r.loc["ST-17", "elev_max_m"], r.loc["ST-17", "prof_max_m"]) == (495.74, 23.82)
    assert r.loc["ST-00", "elev_max_m"] == 532.70 and r.loc["ST-00", "vazao_pico_m3s"] == 26857
    assert np.isnan(r.loc["ST-22", "t_frente_min"]) and r.loc["ST-22", "t_pico_min"] == 165
    r10 = D.sections("PIR", "ruptura_tr10").set_index("secao")
    assert (r10.loc["ST-17", "vazao_pico_m3s"], r10.loc["ST-17", "t_frente_min"]) == (13868, 35)
    assert r10.loc["ST-00", "elev_max_m"] == 531.50


def test_piraju_natural_table_9_spot_values_and_source_oddity():
    n = pd.read_csv(paths.PROCESSED / "dams" / "PIR" / "sections_natural.csv")
    st01 = n[(n.secao == "ST-01") & (n.tr_anos == 10000)].iloc[0]
    assert (st01.prof_max_m, st01.vel_max_ms, st01.elev_max_m) == (20.18, 6.96, 512.18)
    st00 = n[n.secao == "ST-00"].set_index("tr_anos")
    assert st00.vel_max_ms.isna().all()  # '-' no PAE
    assert st00.loc[10, "elev_max_m"] == 532.70 and st00.loc[50, "elev_max_m"] == 531.50  # estranheza da FONTE, mantida


def test_piraju_table_shapes_and_order():
    r = pd.read_csv(paths.PROCESSED / "dams" / "PIR" / "sections_rupture.csv")
    assert len(r) == 46 and r.groupby("tr_anos").secao.nunique().eq(23).all()
    assert (r.select_dtypes("number").dropna() >= 0).all().all()
    assert not r.verified.any()  # OCR + checagens, sem revisão de engenheiro


# ---------------------------------------------------------------- posições e georreferência
def test_river_positions_agree_with_independent_documents():
    v = D.validation()
    assert abs(v["km_osm_piraju_to_paranapanema_dam"] - v["km_pae_piraju_zas"]) < 0.15
    assert v["pos_9_68km_to_official_paranapanema_dam_m"] <= 100
    assert v["piraju_official_vs_jurumirim_st017_m"] <= 100
    assert v["fig17_rms_m"] <= 15 and v["fig17_n_control_points"] >= 12


def test_river_place_rejects_distance_beyond_river():
    from shapely.geometry import LineString, Point
    line = LineString([(0, 0), (1000, 0)])
    assert riverpos.place(line, Point(0, 0), [0.5])["points"][0] == (500.0, 0.0)
    with pytest.raises(ValueError):
        riverpos.place(line, Point(0, 0), [2.0])


@pytest.mark.skipif(not (OCR / "fig17.png").exists(), reason="PNG da Figura 17 é local (gitignored)")
def test_fig17_georef_reproduces_rms():
    import cv2
    g = cv2.cvtColor(cv2.imread(str(OCR / "fig17.png")), cv2.COLOR_BGR2GRAY).astype(float)
    r = fig17.georef(g, json.loads((OCR / "fig17_s1.json").read_text())["items"])
    assert r["rms_m"] < 15 and len(r["labels"]) == 22 and "ST-08" in r["labels"]


def test_dam_positions_have_source_and_are_in_utm_22s_range():
    p = D.dam_points()
    assert set(p.dam) == {"JUR", "PIR", "PAR"} and p.origem.notna().all()
    assert p.x_utm.between(600000, 750000).all() and p.y_utm.between(7.3e6, 7.5e6).all()


# ---------------------------------------------------------------- fatos
def test_facts_have_document_pages_and_no_personal_contacts():
    f = D.facts()
    assert len(f) > 50 and f.source_document.notna().all() and f.page_pdf.notna().all()
    assert not f.astype(str).apply(lambda c: c.str.contains(r"\(\d{2}\) ?\d{4,5}-?\d{4}")).any().any()


def test_known_facts_match_documents():
    f = D.facts().set_index(["dam", "key"])
    assert f.loc[("PIR", "cota_crista_m"), "value_num"] == 534.0 and f.loc[("PIR", "zas_km"), "value_num"] == 9.68
    assert f.loc[("PIR", "cheia_10000_amortecida_m3s"), "page_pdf"] == 45  # p.44 impressa
    assert f.loc[("PAR", "area_mancha_km2"), "value_num"] == 3.4
    assert f.loc[("PIR", "vert_controlado_cap_m3s"), "flag"] == "inconsistencia_da_fonte"


def test_par_scenarios_consistent_with_facts():
    f = D.facts().set_index(["dam", "key"])
    assert D.PAR_SCENARIOS.vazao_m3s.tolist() == [f.loc[("PAR", k), "value_num"] for k in ("cen_tr100", "cen_tr10000", "cen_dam_break", "cen_vertedouros")]


def test_compare_piraju_rupture_not_below_natural_except_known_source_oddity():
    c = D.compare_piraju(10000)
    assert len(c) == 23 and (c.dif_cota_m >= -1e-9).all()
    c10 = D.compare_piraju(10)
    assert (c10[c10.secao != "ST-00"].dif_cota_m >= -1e-9).all()
    assert c10.loc[c10.secao == "ST-00", "dif_cota_m"].iloc[0] == -1.2  # Tabela 9 × 10 divergem no reservatório (FONTE)
    f = D.facts().set_index(["dam", "key"])
    assert f.loc[("PIR", "t9_st00_oddity"), "flag"] == "inconsistencia_da_fonte"  # a estranheza está registrada


def test_paranapanema_has_no_sections():
    assert not D.DAMS["PAR"].has_sections
    with pytest.raises(KeyError):
        D.sections("PAR")
