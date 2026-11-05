from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app"


def _run(rel, timeout=90):
    at = AppTest.from_file(str(APP / rel), default_timeout=timeout).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_home_smoke_and_disclaimer():
    at = _run("Home.py")
    assert any("não substitui o PAE oficial" in w.value for w in at.warning)


@pytest.mark.parametrize("page", ["2_Secoes_da_onda.py", "3_Comparacao.py", "4_Metodo_e_qualidade.py", "6_Cascata_Piraju.py"])
def test_pages_smoke(page):
    at = _run(f"pages/{page}")
    assert any("não substitui o PAE oficial" in w.value for w in at.warning)


def test_map_page_smoke():
    _run("pages/1_Mapa_interativo.py", timeout=180)


def test_report_has_disclaimer():
    from jurumirim import report
    r = report.build_markdown()
    assert "não substitui o PAE oficial" in r and "Piraju" in r


# ---------------------------------------------------------------- filtro de barragens (Isolada × Todas) e simulação
from jurumirim import selection as S  # noqa: E402

FILTERED = ["1_Mapa_interativo.py", "2_Secoes_da_onda.py", "3_Comparacao.py", "4_Metodo_e_qualidade.py",
            "5_Exportacao.py", "7_Simulacao.py"]


def _app(page, dam=None, todas=False, timeout=180):
    at = AppTest.from_file(str(APP / "pages" / page), default_timeout=timeout).run()
    assert not at.exception, [e.value for e in at.exception]
    if todas:
        at.sidebar.radio(key="f_mode").set_value(S.MODE_TODAS).run()
    elif dam:
        at.sidebar.selectbox(key="f_dam").set_value(dam).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


@pytest.mark.parametrize("page", FILTERED)
@pytest.mark.parametrize("dam", ["JUR", "PIR", "PAR"])
def test_pages_work_for_each_isolated_dam(page, dam):
    at = _app(page, dam=dam)
    assert any("não substitui o PAE oficial" in w.value for w in at.warning)


@pytest.mark.parametrize("page", FILTERED)
def test_pages_work_in_all_mode_and_warn_it_is_not_cascade(page):
    at = _app(page, todas=True)
    texts = " ".join(w.value for w in at.warning) + " " + " ".join(c.value for c in at.sidebar.caption)
    assert "cascata" in texts.lower() and "não foi modelada" in texts.lower()


def test_cascade_page_smoke_and_not_modelled_banner():
    at = _run("pages/6_Cascata_Piraju.py", timeout=180)
    assert any("NÃO foi simulada" in e.value for e in at.error)


def test_simulation_page_for_dam_without_sections_stops_with_explanation():
    at = _app("7_Simulacao.py", dam="PAR")
    assert any("Nenhuma barragem selecionada tem tabela" in w.value for w in at.warning)


def test_simulation_time_slider_changes_state_independently_per_dam():
    at = _app("7_Simulacao.py", todas=True)
    at.slider[0].set_value(100).run()
    assert not at.exception
    tab = at.dataframe[0].value  # resumo por barragem em t = 100 min
    assert list(tab["Barragem"]) == ["UHE Jurumirim", "UHE Piraju", "UHE Paranapanema"]
    assert tab.loc[0, "Seções atingidas"] == "12 de 17"   # Jurumirim: relógio próprio
    assert tab.loc[1, "Seções atingidas"] == "22 de 23"   # Piraju: relógio próprio (ST-22 sem tempo no PAE)


def test_interpolation_is_labelled_when_enabled():
    at = _app("7_Simulacao.py", dam="PIR")
    at.checkbox[0].check().run()
    assert any("INTERPOLAÇÃO ILUSTRATIVA" in w.value for w in at.warning)


def test_filter_choice_is_remembered_in_session_state():
    at = _app("2_Secoes_da_onda.py", dam="PIR")
    assert at.session_state["_p_f_dam"] == "PIR"
