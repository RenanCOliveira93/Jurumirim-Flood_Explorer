import numpy as np
import pytest

from jurumirim import exposure as X


def test_force_formulas_match_physics():
    f = X.force_table()
    assert np.allclose(f.pressao_dinamica_kpa, 0.5 * 1000 * f.vel_ms ** 2 / 1000)
    assert np.allclose(f.carga_velocidade_m, f.vel_ms ** 2 / (2 * 9.81))
    pir = f[f.barragem == "Piraju"]
    assert np.allclose(pir.h_x_v_m2s, pir.prof_m * pir.vel_ms, equal_nan=True)
    assert f[f.barragem == "Jurumirim"].prof_m.isna().all()  # Jurumirim não tabela profundidade: não inventar


def test_rupture_has_higher_dynamic_pressure_than_natural_flood_at_same_tr():
    f = X.force_table()
    r = f[f.cenario == "ruptura TR 10000"].set_index("secao").pressao_dinamica_kpa
    n = f[f.cenario == "cheia natural TR 10000"].set_index("secao").pressao_dinamica_kpa
    assert (r / n).dropna().median() > 1


def test_mass_bound_is_volume_over_delta():
    b = X.mass_bound()
    row = b[(b.barragem == "Piraju") & (b.delta_m3s == 1000)].iloc[0]
    assert row.teto_horas == pytest.approx(105.58e6 / 1000 / 3600, abs=0.1)


def test_rise_time_is_peak_minus_arrival_and_never_a_duration():
    r = X.rise_times()
    assert np.allclose(r.subida_ate_o_pico_min, r.pico_min - r.chegada_min, equal_nan=True)  # ST-22 sem chegada tabelada → NaN
    assert not any("dura" in c for c in r.columns)


def test_derived_tables_are_consistent():
    share = X.load("urbana_pct")
    if share.empty:
        pytest.skip("rode make exposure")
    assert np.allclose(share.area_tocada_km2 / share.area_urbanizada_piraju_km2 * 100, share.pct_da_area_urbanizada, atol=0.06)  # áreas gravadas com 4 casas
    assert (share.pct_da_area_urbanizada < 100).all()
    lat = X.load("lateral_transectos")
    assert (lat.avanco_alem_da_margem_m >= 0).all()
    assert ((lat.mancha_m - lat.agua_normal_m).clip(lower=0) - lat.avanco_alem_da_margem_m).abs().max() <= 1  # colunas gravadas arredondadas a 1 m


def test_terrain_extremes_and_layers_are_consistent():
    from jurumirim import terrain3d as T
    w = T.window("piraju")
    e = T.extremes(w)
    assert e["baixo"][2] < e["alto"][2] and e["alto"][2] == pytest.approx(float(np.nanmax(w["z"])))
    L = T.layers(w, ("pir", "normal"))
    assert L["pir"]["mask"].shape == w["z"].shape and L["pir"]["mask"].any()
    # tempo de chegada só existe onde há água e nunca é negativo
    t = L["pir"]["t_arr"]; assert np.isnan(t[~L["pir"]["mask"]]).all() and np.nanmin(t) >= 0
    # a cota da água estimada nunca fica abaixo do terreno que ela cobre (condição do enchimento)
    zw = L["pir"]["z_water"]; ok = L["pir"]["mask"]
    assert (zw[ok] >= w["z"][ok] - 1e-6).all()


def test_documentation_numbers_match_derived_data():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    doc = (root / "docs" / "GUIA_TECNICO.md").read_text(encoding="utf-8")
    m = json.loads((root / "data" / "processed" / "dams" / "PIR" / "estimativa_metricas.json").read_text())
    assert f"{m['ruptura_tr10000']['area_total_km2']:.1f}".replace(".", ",") + " km²" in doc
    val = m["validacao_fig17_natural_tr10000"]
    assert f"{100 * val['cobertura_da_mancha_clara_sem_tolerancia']:.1f}".replace(".", ",") + " %" in doc
    for ref in ("d3ltu4sfk36jla.cloudfront.net/cba/PIRAJU_TARJADO_para_site_76f2c48308.pdf",
                "d3ltu4sfk36jla.cloudfront.net/cba/PSB_Sumario_Executivo_UHE_Piraju_fd580524df.pdf",
                "ctgbr.com.br/sustentabilidade/social/seguranca-da-comunidade/pae/pae-arquivos",
                "enel.com.br/pt-saopaulo/quemsomos/archive/d2018-comportamento-etico/plano-de-acao-de-emergencia.html"):
        assert ref in doc
