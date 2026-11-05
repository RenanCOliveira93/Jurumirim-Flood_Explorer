import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, data, footer, setup, sidebar_filter, st, tag  # noqa: E402

import plotly.graph_objects as go  # noqa: E402

setup("Comparação: ruptura × cheia sem ruptura")
sel = sidebar_filter()
if sel.is_all:
    st.warning(S.NOT_CASCADE + " As comparações abaixo são sempre DENTRO de cada barragem (ruptura × cheia natural do mesmo PAE).")

# ------------------------------------------------------------------ Jurumirim (conteúdo original, inalterado)
if "JUR" in sel.dam_ids:
    st.header("UHE Jurumirim")
    st.markdown(tag("DERIVADO") + "  Comparação restrita ao nível de detalhe do PAE (prancha p. 38).", unsafe_allow_html=True)
    p = data.polygons()
    a = p.groupby("classe").area_km2.sum()
    st.table({
        "Cenário": ["Ruptura isolada em dia seco (envoltória ZAS+ZSS)", "ZAS implantada", "Cheia de projeto TR=10.000 anos, sem ruptura"],
        "Área digitalizada (km²)": [round(a["ENVOLTORIA_RUPTURA"], 2), round(a["ZAS"], 2), round(a["CHEIA_SR"], 2)],
        "Confiança da digitalização": ["média", "média", "baixa"],
        "Fonte": ["PAE p. 38"] * 3,
    })
    st.warning(
        "O PAE **não** fornece, para o cenário sem ruptura, tabela de sobrelevação, velocidade nem tempo — somente o contorno azul. "
        "Portanto não há comparação de parâmetros hidráulicos entre os dois cenários. A cheia sem ruptura é a envoltória de "
        "referência do próprio reservatório/rio; a diferença de áreas abaixo é **indicativa**, limitada pela baixa confiança do "
        "traçado azul (linha alterada sob o tom vermelho da ZAS e sobreposta ao reservatório)."
    )
    env_a, ch = a["ENVOLTORIA_RUPTURA"], a["CHEIA_SR"]
    st.metric("Razão envoltória de ruptura / cheia sem ruptura (indicativa)", f"{env_a/ch:.1f}×")
    st.markdown(tag("ESTIMATIVA") + " razão entre áreas digitalizadas; não é razão de profundidade ou de dano.", unsafe_allow_html=True)

# ------------------------------------------------------------------ Piraju
if "PIR" in sel.dam_ids:
    st.header("UHE Piraju")
    tr = 10 if sel.scenario("PIR") == "ruptura_tr10" else 10000
    tr_txt = f"{tr:,}".replace(",", ".")
    st.markdown(tag("OFICIAL") + f"  PAE UHE Piraju: **Tabela 10** (ruptura) × **Tabela 9** (sem ruptura), mesma TR = {tr_txt} anos, "
                "mesma seção (p. 61–62 impressas).", unsafe_allow_html=True)
    cmp_ = D.compare_piraju(tr)
    st.dataframe(cmp_.rename(columns={
        "secao": "Seção", "distancia_km": "Dist. (km)", "elev_max_ruptura_m": "Cota máx. ruptura (m)",
        "elev_max_natural_m": "Cota máx. sem ruptura (m)", "prof_max_ruptura_m": "Prof. ruptura (m)",
        "prof_max_natural_m": "Prof. sem ruptura (m)", "vel_max_ruptura_ms": "Vel. ruptura (m/s)",
        "vel_max_natural_ms": "Vel. sem ruptura (m/s)", "dif_cota_m": "Δ cota (m)"}), hide_index=True, width="stretch")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cmp_.distancia_km, y=cmp_.dif_cota_m, mode="lines+markers", text=cmp_.secao, name="Δ cota máx.",
                             line=dict(color=D.COLORS["PIR"])))
    fig.add_vline(x=9.68, line=dict(dash="dash", color="#555"), annotation_text="UHE Paranapanema / fim da ZAS (9,68 km)")
    fig.update_layout(height=340, xaxis_title="Distância ao eixo da barragem (km)",
                      yaxis_title="Cota máx. ruptura − sem ruptura (m)")
    st.plotly_chart(fig, width="stretch")
    if tr == 10:
        st.caption("ST-00 (reservatório): a Tabela 9 dá 532,70 m para TR 10 anos, valor que difere do N.A. inicial de 531,50 m da "
                   "Tabela 10 (e é maior que o de TR 50 anos). Inconsistência da fonte, mantida como publicada.")
    st.info("Δ cota = diferença entre duas colunas publicadas no PAE, seção a seção. **Não** indica quais terrenos, imóveis "
            "ou vias seriam alcançados (a mancha georreferenciada de Piraju não consta do PDF). ST-12 (km 9,86) em diante "
            "ficam a jusante da posição da UHE Paranapanema (km 9,68, PAE Piraju p. 63 impressa).")

# ------------------------------------------------------------------ Paranapanema
if "PAR" in sel.dam_ids:
    st.header("UHE Paranapanema")
    st.markdown(tag("OFICIAL") + "  PAE UHE Paranapanema, seção 9 (p. 14): cenários HEC-RAS como publicados.", unsafe_allow_html=True)
    st.dataframe(D.PAR_SCENARIOS.rename(columns={"cenario": "Cenário", "vazao_m3s": "Vazão (m³/s)", "na_montante_m": "N.A. montante (m)",
                                                 "source_document": "Documento", "source_page": "Página"}),
                 hide_index=True, width="stretch")
    st.info("Segundo o próprio PAE (p. 17): «cheias naturais mais desfavoráveis que a própria ruptura apesar do volume do reservatório» "
            "(reservatório de ≈ 12,2 hm³). Área diretamente afetada ≈ 3,4 km²; ZAS = 10 km a jusante. O PDF **não** inclui os mapas "
            "(Anexos 1–2) nem tabela de tempos por seção.")
footer("Cada comparação usa dois cenários do MESMO PAE; nada é somado entre barragens.")
