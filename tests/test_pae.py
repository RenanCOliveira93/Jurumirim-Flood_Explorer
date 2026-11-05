import json

import pandas as pd
import pytest

from jurumirim.pae import extract_sections, hhmm_to_minutes, parse_br_number
from jurumirim.paths import METADATA, PROCESSED


@pytest.fixture(scope="module")
def sec():
    return extract_sections()


def test_parse_br_number():
    assert parse_br_number("7.432.016") == 7432016.0
    assert parse_br_number("29,72") == 29.72
    assert parse_br_number("42.728") == 42728.0
    assert parse_br_number("-") is None


def test_hhmm():
    assert hhmm_to_minutes("01:59") == 119
    assert hhmm_to_minutes("00:01") == 1
    for bad in ("1:99", "abc", "00:60"):
        with pytest.raises(ValueError):
            hhmm_to_minutes(bad)


def test_17_sections_sorted(sec):
    assert list(sec.id) == [f"ST-{i:03d}" for i in range(1, 18)]


def test_known_values_checked_against_image(sec):
    r = sec.set_index("id")
    assert r.loc["ST-001", ["sobrelevacao_m", "velocidade_ms", "vazao_pico_m3s"]].tolist() == [29.72, 9.46, 42728.0]
    assert r.loc["ST-006", "tempo_chegada_hhmm"] == "00:31" and r.loc["ST-006", "distancia_km"] == 6.71
    assert r.loc["ST-014", "x_utm"] == 667050.0 and r.loc["ST-014", "y_utm"] == 7436709.0
    assert r.loc["ST-017", "tempo_chegada_min"] == 119


def test_ranges_and_monotonicity(sec):
    assert sec.distancia_km.is_monotonic_increasing
    assert sec.tempo_chegada_min.is_monotonic_increasing
    assert sec.sobrelevacao_m.is_monotonic_decreasing
    assert sec.distancia_km.between(0, 33).all()
    assert sec.velocidade_ms.between(1, 10).all()
    assert sec.x_utm.between(660000, 690000).all() and sec.y_utm.between(7.42e6, 7.45e6).all()


def test_missing_flow_is_nan_not_guess(sec):
    assert pd.isna(sec.set_index("id").loc["ST-017", "vazao_pico_m3s"])
    assert sec.vazao_pico_m3s.dropna().between(19000, 43000).all()


def test_csv_matches_extraction(sec):
    csv = pd.read_csv(PROCESSED / "pae_sections.csv")
    assert csv.id.tolist() == sec.id.tolist()
    assert (csv.sobrelevacao_m == sec.sobrelevacao_m).all()


def test_provenance_file():
    p = json.loads((METADATA / "pae_provenance.json").read_text())
    assert p["fonte_primaria"]["pagina_fisica_pdf"] == 38
    assert p["georreferenciamento"]["rms_m"] < 2
    assert "CHEIA_SR" in p["vetorizacao"]["qualidade_por_classe"]


FIG12_P55 = ["00:01", "00:03", "00:09", "00:13", "00:21", "00:31", "00:37", "00:45", "00:56",
             "01:09", "01:21", "01:39", "01:49", "01:55", "01:57", "01:59", "01:59"]


def test_arrival_times_match_independent_figure12_p55(sec):
    """Transcrição visual da Figura 12 (PDF p. 55) × quadro da prancha (PDF p. 38)."""
    assert sec.tempo_chegada_hhmm.tolist() == FIG12_P55
