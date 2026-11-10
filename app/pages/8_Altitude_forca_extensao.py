import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, data, footer, setup, st, tag  # noqa: E402

import plotly.graph_objects as go  # noqa: E402

from jurumirim import exposure as X  # noqa: E402

setup("Altitude, força, extensão e duração")
st.markdown(tag("DERIVADO") + " " + tag("ESTIMATIVA") + "  Respostas calculadas **só com valores tabelados nos PAEs e com o relevo**. "
            "Não é simulação hidráulica, não classifica imóveis/endereços/rotas e não estima probabilidade de ruptura. "
            "Onde depende da mancha estimada de Piraju, está marcado como ESTIMATIVA.", unsafe_allow_html=True)

force, lat, latsum = X.load("forca"), X.load("lateral_transectos"), X.load("lateral_resumo")
share, alt = X.load("urbana_pct"), X.load("urbana_altitude")
rise, bound = X.load("tempo_subida"), X.load("tempo_teto_massa")
if force.empty:
    st.error("Tabelas derivadas ausentes. Rode `make exposure`.")
    st.stop()

t1, t2, t3, t4, t5 = st.tabs(["1. Altitude e força", "2. Quantos metros para os lados", "3. % da área urbana", "4. Altitude × nível da água", "5. Por quanto tempo?"])

with t1:
    st.markdown("**Como comparar a «força» da água.** O PAE tabela, por seção, a velocidade máxima (e, em Piraju, a profundidade). Daí saem: "
                "**pressão dinâmica** ½·ρ·v² (kPa), **carga de velocidade** v²/2g (m de queda equivalente) e o índice **h·v** (m²/s).")
    cen = st.multiselect("Cenários", sorted(force.cenario.unique()), default=["ruptura (568,00 m)", "ruptura TR 10000", "cheia natural TR 10000"])
    f = force[force.cenario.isin(cen)]
    fig = go.Figure()
    for c, g in f.groupby("cenario"):
        g = g.sort_values("km")
        fig.add_trace(go.Scatter(x=g.km, y=g.pressao_dinamica_kpa, mode="lines+markers", name=c, text=g.secao,
                                 hovertemplate="%{text} · km %{x:.2f}<br>%{y:.1f} kPa<extra>" + "%{fullData.name}" + "</extra>"))
    fig.update_layout(height=380, xaxis_title="Distância ao longo do rio (km) — a partir de cada barragem", yaxis_title="Pressão dinâmica ½ρv² (kPa)",
                      legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")
    res = (f.groupby("cenario").agg(vel_max_ms=("vel_ms", "max"), vel_mediana_ms=("vel_ms", "median"), pressao_max_kpa=("pressao_dinamica_kpa", "max"),
                                    carga_max_m=("carga_velocidade_m", "max"), h_x_v_max=("h_x_v_m2s", "max")).round(1).reset_index())
    st.dataframe(res.rename(columns={"cenario": "Cenário", "vel_max_ms": "v máx. (m/s)", "vel_mediana_ms": "v mediana (m/s)",
                                     "pressao_max_kpa": "Pressão dinâmica máx. (kPa)", "carga_max_m": "Carga de velocidade máx. (m)", "h_x_v_max": "h·v máx. (m²/s)"}),
                 hide_index=True, width="stretch")
    r10 = force[force.cenario == "ruptura TR 10000"].set_index("secao"); n10 = force[force.cenario == "cheia natural TR 10000"].set_index("secao")
    ratio = (r10.pressao_dinamica_kpa / n10.pressao_dinamica_kpa).dropna()
    if len(ratio):
        st.info(f"**Piraju, TR 10.000:** a pressão dinâmica da ruptura é, na mediana das seções, **{ratio.median():.1f}×** a da cheia natural do mesmo TR "
                f"(de {ratio.min():.1f}× a {ratio.max():.1f}×). Jurumirim e Piraju vêm de estudos diferentes: comparar os números entre eles mostra ordem de grandeza, "
                "não que uma onda se soma à outra.")
    st.caption("**Limites:** são valores **máximos na seção do canal** (HEC-RAS). Não são a velocidade nem a pressão sobre o terreno ou sobre construções; "
               "não incluem detritos nem sedimentos. Jurumirim não tem profundidade tabelada (só sobrelevação). Piraju: leitura por OCR, sem revisão de engenheiro. "
               "Paranapanema: o PDF não traz velocidade por seção.")

with t2:
    st.markdown("**Quantos metros a água avançaria além da margem do rio normal?** Em transectos perpendiculares ao eixo (a cada 500 m), "
                "medi a borda da mancha e subtraí a borda da **água normal** (OSM). Valor = avanço para fora da margem atual, por margem.")
    sc = st.selectbox("Cenário", sorted(lat.cenario.unique()), index=sorted(lat.cenario.unique()).index("PIR estimativa ruptura TR 10000"))
    g = lat[lat.cenario == sc]
    fig = go.Figure()
    for m, c in (("esquerda", "#1f77b4"), ("direita", "#d62728")):
        q = g[g.margem == m]
        fig.add_trace(go.Scatter(x=q.km, y=q.avanco_alem_da_margem_m, mode="lines", name=f"margem {m}", line=dict(color=c)))
    fig.update_layout(height=340, xaxis_title="km ao longo do eixo do rio (ILUSTRAÇÃO)", yaxis_title="Avanço além da margem normal (m)", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(latsum.rename(columns={"cenario": "Cenário", "transectos": "Transectos", "mediana_m": "Mediana (m)", "p90_m": "90 % (m)",
                                        "maximo_m": "Máximo (m)", "largura_total_mediana_m": "Largura total mediana (m)"}), hide_index=True, width="stretch")
    st.caption("**Ler assim:** «mediana 56 m» = em metade dos pontos do vale a água passaria menos de 56 m da margem normal; o máximo mostra os alargamentos do vale "
               "(1 km = 1.000 m). Jurumirim = mancha **oficial** do PAE (p. 38); Piraju = **estimativa exploratória**. A largura de Jurumirim é maior porque o cenário "
               "(pico 42.728 m³/s) é outro. Posição do eixo: OSM (±dezenas de m); relevo 30 m.")

with t3:
    st.markdown("**Qual o percentual da área urbana atingida?** Base: áreas urbanizadas IBGE 2019 dentro do município de Piraju (≠ perímetro urbano legal).")
    s = share.rename(columns={"cenario": "Cenário", "area_urbanizada_piraju_km2": "Área urbanizada de Piraju (km²)", "area_tocada_km2": "Área tocada (km²)",
                              "pct_da_area_urbanizada": "% da área urbanizada", "poligonos_tocados": "Manchas tocadas", "poligonos_total": "Manchas (total)"})
    st.dataframe(s, hide_index=True, width="stretch")
    jr = share[share.cenario.str.contains("envoltória")].iloc[0]; pr = share[share.cenario == "PIR estimativa ruptura TR 10000"].iloc[0]
    c1, c2 = st.columns(2)
    c1.metric("Jurumirim (mancha oficial)", f"{jr.pct_da_area_urbanizada:.2f} %", f"{jr.area_tocada_km2*1e6:,.0f} m²".replace(",", "."), delta_color="off")
    c2.metric("Piraju, ruptura TR 10.000 (ESTIMATIVA)", f"{pr.pct_da_area_urbanizada:.2f} %", f"{pr.area_tocada_km2*1e6:,.0f} m²".replace(",", "."), delta_color="off")
    st.caption("São cenários **isolados**: não somar. O PAE de Piraju informa **84 edificações na ZAS** (p. 63), dado oficial que não depende desta estimativa. "
               "Os percentuais medem **área de mancha urbanizada IBGE tocada**, não pessoas, imóveis nem endereços, e não classificam nada como seguro ou inseguro.")

with t4:
    st.markdown("**Altitude dos locais × nível máximo da água.** Relevo (Copernicus 30 m, MDS) de cada mancha urbanizada IBGE a até 3 km do rio, "
                "comparado à **cota máxima tabelada** no PAE de Piraju na seção mais próxima.")
    sec = D.sections("PIR", "ruptura_tr10000"); nat = D.natural_sections(10000)
    sec = sec[sec.secao != "ST-00"]
    fig = go.Figure()
    base = D.compare_piraju(10000)
    base = base[base.secao != "ST-00"]
    fig.add_trace(go.Scatter(x=base.distancia_km, y=base.elev_max_ruptura_m, mode="lines+markers", name="cota máx. — ruptura (T10)", line=dict(color="#8b0000")))
    fig.add_trace(go.Scatter(x=base.distancia_km, y=base.elev_max_natural_m, mode="lines+markers", name="cota máx. — cheia natural (T9)", line=dict(color="#1565c0")))
    fund = base.elev_max_ruptura_m - base.prof_max_ruptura_m
    fig.add_trace(go.Scatter(x=base.distancia_km, y=fund, mode="lines", name="fundo do canal (cota − profundidade)", line=dict(color="#555", dash="dot")))
    fig.update_layout(height=340, xaxis_title="km a jusante de Piraju", yaxis_title="Altitude (m)", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")
    a = alt[["id_poligono", "densidade", "area_km2", "dist_ao_rio_m", "alt_min_m", "alt_mediana_m", "alt_max_m",
             "cota_agua_ruptura_tr10000_m", "folga_ruptura_tr10000_m", "pct_celulas_abaixo_cota_ruptura_tr10000",
             "folga_natural_tr10000_m"]].rename(columns={
        "id_poligono": "Mancha IBGE", "densidade": "Densidade", "area_km2": "Área (km²)", "dist_ao_rio_m": "Dist. ao rio (m)",
        "alt_min_m": "Alt. mín. (m)", "alt_mediana_m": "Alt. mediana (m)", "alt_max_m": "Alt. máx. (m)",
        "cota_agua_ruptura_tr10000_m": "Cota máx. da água, ruptura (m)", "folga_ruptura_tr10000_m": "Folga: alt. mín. − cota (m)",
        "pct_celulas_abaixo_cota_ruptura_tr10000": "% do terreno abaixo da cota", "folga_natural_tr10000_m": "Folga, cheia natural (m)"})
    st.dataframe(a, hide_index=True, width="stretch")
    st.caption("**Folga > 0:** o ponto mais baixo da mancha fica acima da cota máxima da água naquela seção; **< 0:** há terreno abaixo dela. "
               "«% do terreno abaixo da cota» **não exige conexão com o rio**, então é um teto: a estimativa conectada (aba 3) é menor. "
               "A cota usa a seção mais próxima do **ponto central** da mancha (aproximação; manchas grandes variam), a posição das seções é ILUSTRATIVA, "
               "e a cota do PAE e a do relevo podem ter referenciais verticais diferentes. Jurumirim não tabela cota máxima (só sobrelevação), então não há esta comparação para ela.")

with t5:
    st.markdown("**É possível dizer por quanto tempo ficaria inundado? Não, com os documentos disponíveis.**")
    st.error("Os PAEs tabelam **quando a água chega** e **quando atinge o pico**, mas **não trazem o hidrograma completo nem a descida do nível**. "
             "Sem a recessão não há como calcular a duração da inundação, e eu não vou inventar um número.")
    st.markdown("**O que é documentado** (Piraju, Tabela 10): chegada, pico e a **subida até o pico**. Jurumirim tabela só a chegada.")
    r = rise[rise.cenario == st.selectbox("Cenário de Piraju", sorted(rise.cenario.unique()), index=1)]
    st.dataframe(r.rename(columns={"secao": "Seção", "km": "km", "chegada_min": "Chegada (min)", "pico_min": "Pico (min)",
                                   "subida_ate_o_pico_min": "Subida até o pico (min)"}).drop(columns=["barragem", "cenario"]), hide_index=True, width="stretch")
    st.markdown("**O único limite que se pode afirmar** (conservação de massa, não é estimativa de duração): a água liberada não passa do volume do reservatório, "
                "logo a vazão não pode ficar **Δ acima da base** por mais de V/Δ.")
    st.dataframe(bound.rename(columns={"barragem": "Barragem", "volume_hm3": "Volume (hm³)", "delta_m3s": "Δ acima da base (m³/s)", "teto_horas": "Teto (h)"}),
                 hide_index=True, width="stretch")
    st.caption("Em Piraju (105,58 hm³) o teto é de horas. Em Jurumirim ele passa de dias e **não informa nada**, porque o volume acima do fundo da brecha não consta do PAE. "
               "Um teto não é a duração: o tempo real seria menor, e a água também pode **permanecer em baixadas** depois que a onda passa. "
               "Para saber a duração, é preciso o hidrograma de ruptura e a modelagem hidráulica do estudo original (peça à CBA/CTG).")

footer("Fontes: PAEs de Jurumirim (p. 38) e Piraju (Tabelas 9 e 10, OCR), IBGE 2019, Copernicus GLO-30, OSM. Estimativa de Piraju: ver docs/GUIA_TECNICO.md.")
