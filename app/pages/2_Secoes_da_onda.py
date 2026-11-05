import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, data, footer, setup, sidebar_filter, st, tag  # noqa: E402

import plotly.graph_objects as go  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

from jurumirim import dam_plots  # noqa: E402

setup("Seções da onda")
sel = sidebar_filter()
if sel.is_all:
    st.warning(S.NOT_CASCADE)

# ------------------------------------------------------------------ Jurumirim (conteúdo original, inalterado)
if "JUR" in sel.dam_ids:
    st.header("UHE Jurumirim")
    s = data.sections()
    st.markdown(tag("OFICIAL") + "  Valores do quadro de seções, **PAE PDF p. 38** (cenário: ruptura isolada em dia seco, N.A. 568,00 m).",
                unsafe_allow_html=True)
    st.caption("Tempo de chegada = instante em que a onda atinge sobrelevação de 0,61 m (~2 ft) — nota 2 da prancha.")

    show = s[["id", "descricao", "distancia_km", "tempo_chegada_hhmm", "sobrelevacao_m", "velocidade_ms", "vazao_pico_m3s"]].copy()
    show.columns = ["Seção", "Descrição", "Dist. (km)", "Chegada (hh:mm)", "Sobrelev. (m)", "Veloc. (m/s)", "Vazão pico (m³/s)"]
    show["Fonte"] = "PAE p. 38"
    st.dataframe(show, hide_index=True, width="stretch")

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Tempo de chegada (min)", "Sobrelevação (m)", "Velocidade (m/s)", "Vazão de pico (m³/s)"))
    for (r, c), col in zip([(1, 1), (1, 2), (2, 1), (2, 2)], ["tempo_chegada_min", "sobrelevacao_m", "velocidade_ms", "vazao_pico_m3s"]):
        fig.add_trace(go.Scatter(x=s.distancia_km, y=s[col], mode="lines+markers", text=s.id, hovertemplate="%{text}<br>%{x} km<br>%{y}"),
                      row=r, col=c)
        fig.update_xaxes(title_text="Distância (km)", row=r, col=c)
    fig.update_yaxes(type="log", row=2, col=2)
    fig.update_layout(height=620, showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Linha do tempo (somente seções documentadas)")
    t = st.slider("Tempo após a ruptura hipotética (min)", 0, 125, 60, 1)
    arrived = s[s.tempo_chegada_min <= t]
    st.write(f"{len(arrived)} de {len(s)} seções já atingidas pela frente da onda (sobrelevação ≥ 0,61 m) até {t//60}h{t%60:02d}.")
    tl = go.Figure()
    tl.add_trace(go.Scatter(x=s.distancia_km, y=[0] * len(s), mode="markers+text", text=s.id.str[3:], textposition="top center",
                            marker=dict(size=14, color=["#d62728" if a else "#bbb" for a in (s.tempo_chegada_min <= t)])))
    tl.update_yaxes(visible=False, range=[-1, 1]); tl.update_xaxes(title="Distância ao longo do rio (km)")
    tl.update_layout(height=200, margin=dict(t=10))
    st.plotly_chart(tl, width="stretch")
    st.markdown(tag("OFICIAL") + " marcadores nos tempos tabelados. Sem interpolação entre seções.", unsafe_allow_html=True)

# ------------------------------------------------------------------ Piraju
for dam, sc in sel.with_sections():
    if dam != "PIR":
        continue
    st.header("UHE Piraju")
    s = D.sections("PIR", sc)
    lbl = D.sel_label("PIR", sc).split(" — ")[-1]
    st.markdown(tag("OFICIAL") + f"  **PAE UHE Piraju, Tabela 10 (p. 62 impressa / 63 PDF)** — {lbl}. "
                "Transcrição por OCR com checagens (ver *Método e qualidade*).", unsafe_allow_html=True)
    st.caption("'Chegada da onda' = tempo de início da onda de ruptura; 'até o pico' = tempo até a vazão máxima na seção "
               "(texto do PAE, p. 61 impressa). Distância medida do eixo da barragem de Piraju. A ZAS vai até 9,68 km "
               "(UHE Paranapanema), mas a tabela segue até 32,35 km.")
    show = s[["secao", "distancia_km", "t_frente_min", "t_pico_min", "vazao_pico_m3s", "vel_max_ms", "prof_max_m", "elev_max_m"]].copy()
    show.columns = ["Seção", "Dist. (km)", "Chegada da onda (min)", "Até o pico (min)", "Vazão máx. (m³/s)", "Veloc. máx. (m/s)",
                    "Prof. máx. (m)", "Cota máx. (m)"]
    show["Fonte"] = "PAE Piraju p. 62 (impr.)"
    st.dataframe(show, hide_index=True, width="stretch")
    st.caption("ST-22 não tem 'chegada da onda' ('-' no PAE); a vazão de ST-22 vem com asterisco sem nota na página. "
               "A vazão de pico não é monotônica no PAE (sobe entre ST-09 e ST-10 nos dois TR); mantida como publicada.")
    dfp = S.sections_for(S.make(S.MODE_ISOLADA, ["PIR"], {"PIR": sc}))
    st.plotly_chart(dam_plots.section_panels(dfp), width="stretch")

# ------------------------------------------------------------------ Paranapanema
for dam in sel.without_sections():
    st.header(D.DAMS[dam].name)
    st.info(D.DAMS[dam].note + " Veja os cenários HEC-RAS na página *Comparação* e os fatos em *Cascata Piraju*.")

# ------------------------------------------------------------------ visão combinada
if sel.is_all and len(sel.with_sections()) > 1:
    st.header("Visão combinada (relógios independentes)")
    st.plotly_chart(dam_plots.section_panels(S.sections_for(sel)), width="stretch")
    st.caption("Cada curva usa a distância ao eixo da PRÓPRIA barragem e o tempo desde a ruptura DESSA barragem. "
               "Não indica que a onda de uma rompe a outra.")
footer("Não são resultados de simulação própria.")
