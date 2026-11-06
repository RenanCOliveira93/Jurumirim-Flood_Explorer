import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st  # noqa: E402

from jurumirim import DISCLAIMER, data  # noqa: E402
from jurumirim import dams as D  # noqa: E402
from jurumirim import selection as S  # noqa: E402

TAGS = {
    "OFICIAL": ("DADO OFICIAL", "#1b5e20"),
    "DERIVADO": ("DERIVADO DO PAE", "#0d47a1"),
    "ESTIMATIVA": ("ESTIMATIVA EXPLORATÓRIA", "#e65100"),
    "ILUSTRACAO": ("ILUSTRAÇÃO", "#6a1b9a"),
}


def tag(key: str) -> str:
    text, color = TAGS[key]
    return (f"<span style='background:{color};color:#fff;padding:2px 8px;border-radius:4px;"
            f"font-size:.75rem;font-weight:600'>{text}</span>")


def setup(title: str):
    st.set_page_config(page_title=f"{title} — Jurumirim Flood Explorer", page_icon="🌊", layout="wide")
    st.warning(f"⚠️ {DISCLAIMER}")
    st.title(title)


def footer(extra: str = ""):
    st.divider()
    st.caption(f"Fonte: {data.SRC_TABLE}. {extra}  \n{DISCLAIMER}")


def _restore(key, default):
    """O Streamlit descarta o estado de widget ao trocar de página; reaplica o último valor escolhido."""
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get("_p_" + key, default)


def _keep(key):
    st.session_state["_p_" + key] = st.session_state[key]


def sidebar_filter() -> S.Selection:
    """Filtro global: 'Por Barragem Isolada' × 'Todas barragens selecionadas' (+ cenário por barragem)."""
    ids = list(D.DAMS)
    name = lambda i: D.DAMS[i].name  # noqa: E731
    with st.sidebar:
        st.markdown("### Barragens")
        _restore("f_mode", S.MODE_ISOLADA)
        mode = st.radio("Visualizar", S.MODES, key="f_mode", help="'Todas' sobrepõe cenários ISOLADOS; não é cascata.")
        _keep("f_mode")
        if mode == S.MODE_ISOLADA:
            _restore("f_dam", "JUR")
            chosen = [st.selectbox("Barragem", ids, format_func=name, key="f_dam")]
            _keep("f_dam")
        else:
            _restore("f_dams", ids)
            chosen = st.multiselect("Barragens", ids, format_func=name, key="f_dams")
            _keep("f_dams")
            if not chosen:
                st.warning("Selecione ao menos uma barragem.")
                chosen = ids
        scen = {}
        multi = [d for d in chosen if len(D.DAMS[d].scenarios) > 1]
        if multi:
            with st.expander("Cenário por barragem", expanded=True):
                for d in multi:
                    opts = [s_.id for s_ in D.DAMS[d].scenarios]
                    _restore(f"f_sc_{d}", opts[0])
                    scen[d] = st.selectbox(name(d), opts, key=f"f_sc_{d}",
                                           format_func=lambda i, d=d: next(s_.label for s_ in D.DAMS[d].scenarios if s_.id == i))
                    _keep(f"f_sc_{d}")
        chain = False
        if mode == S.MODE_TODAS:
            _restore("f_chain", False)
            chain = st.checkbox("Encadear no tempo (hipótese de ruptura sequencial)", key="f_chain",
                                help="Cada barragem rompe quando chega a onda da anterior (tempo do PAE). Só desloca relógios; ILUSTRAÇÃO.")
            _keep("f_chain")
            st.caption("⚠️ " + (S.CHAIN_BANNER if chain else S.NOT_CASCADE))
    return S.make(mode, chosen, scen, chain=chain)
