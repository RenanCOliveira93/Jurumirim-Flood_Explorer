import numpy as np
import pandas as pd
import pytest

from jurumirim import dams as D
from jurumirim import selection as S


def test_isolada_keeps_only_one_dam_in_given_order():
    s = S.make(S.MODE_ISOLADA, ["PIR", "JUR"])
    assert s.dam_ids == ["PIR"] and not s.is_all


def test_todas_orders_by_cascade_and_applies_scenarios():
    s = S.make(S.MODE_TODAS, ["PAR", "PIR", "JUR"], {"PIR": "ruptura_tr10"})
    assert s.dam_ids == ["JUR", "PIR", "PAR"] and s.scenario("PIR") == "ruptura_tr10" and s.scenario("PAR") is None
    assert s.without_sections() == ["PAR"] and [d for d, _ in s.with_sections()] == ["JUR", "PIR"]


@pytest.mark.parametrize("bad", [dict(mode="x", chosen=["JUR"]), dict(mode=S.MODE_TODAS, chosen=[]), dict(mode=S.MODE_TODAS, chosen=["XXX"])])
def test_invalid_selection_raises(bad):
    with pytest.raises(ValueError):
        S.make(bad["mode"], bad["chosen"])


def test_default_scenario_is_the_conservative_one():
    assert S.make(S.MODE_ISOLADA, ["PIR"]).scenario("PIR") == "ruptura_tr10000"


def test_sections_for_adds_labels_and_skips_dams_without_sections():
    s = S.sections_for(S.make(S.MODE_TODAS, ["JUR", "PIR", "PAR"]))
    assert set(s.dam) == {"JUR", "PIR"} and len(s) == 17 + 23 and s.label.notna().all()


def test_all_mode_is_overlay_with_independent_clocks_not_cascade():
    """O estado de Piraju em t não pode depender de Jurumirim estar selecionada: relógios independentes."""
    t = 30
    alone = S.state_at(S.make(S.MODE_ISOLADA, ["PIR"]), t)
    both = S.state_at(S.make(S.MODE_TODAS, ["JUR", "PIR"]), t)
    both = both[both.dam == "PIR"].reset_index(drop=True)
    pd.testing.assert_frame_equal(alone.reset_index(drop=True), both)
    # Jurumirim leva 119 min até ST-017; Piraju (ruptura própria) já chegou a 14,6 km em ~30 min: sem acoplamento
    assert (alone[alone.estado == "atingida"].distancia_km.max()) > 14


def test_state_semantics_reached_not_reached_unknown():
    s = S.state_at(S.make(S.MODE_ISOLADA, ["PIR"]), 10_000)
    assert (s.estado == "sem tempo no PAE").sum() == 1 and s[s.estado == "sem tempo no PAE"].secao.iloc[0] == "ST-22"
    s0 = S.state_at(S.make(S.MODE_ISOLADA, ["PIR"]), 0)
    assert s0[s0.estado == "atingida"].secao.tolist() == ["ST-00"]  # t_frente = 0 só no eixo


def test_t_max_and_summary():
    assert S.t_max(S.make(S.MODE_ISOLADA, ["JUR"])) == 119
    assert S.t_max(S.make(S.MODE_ISOLADA, ["PAR"])) == 0
    sm = S.summary_at(S.make(S.MODE_TODAS, ["JUR", "PIR", "PAR"]), 119)
    assert sm.shape[0] == 3 and sm.loc[0, "secoes_atingidas"] == "17 of 17".replace("of", "de")
    assert "sem tabela" in sm.loc[2, "secoes_atingidas"]


def test_front_km_interpolates_inside_and_never_extrapolates():
    df = D.sections("PIR", "ruptura_tr10000")
    assert S.front_km(df, 3.5) is not None and 0 <= S.front_km(df, 3.5) <= 1.0
    assert S.front_km(df, -1) is None and S.front_km(df, 10_000) is None
    k = [S.front_km(df, t) for t in range(1, 84)]
    assert np.all(np.diff(k) >= -1e-9)  # monotônica


def test_coverage_notes_state_what_is_missing():
    n = " ".join(S.coverage_notes(S.make(S.MODE_TODAS, ["PIR", "PAR"])))
    assert "indisponível" in n and "Apêndice 9" in n
