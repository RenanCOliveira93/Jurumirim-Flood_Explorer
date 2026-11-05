from common import data, footer, setup, st, tag

setup("Visão geral")
ov = data.overlap_tables()
prov = data.provenance()

st.markdown(
    "Projeto independente que investiga, **com base exclusivamente nos PAEs oficiais** (UHE Jurumirim; Piraju e Paranapanema acrescentados depois), "
    "a lenda de que uma ruptura da barragem inundaria toda a cidade de Piraju-SP. "
    "Não há simulação hidráulica própria aqui: tudo é reprodução/análise espacial do que o PAE publica."
)
st.subheader("Cenário oficial")
c1, c2, c3 = st.columns(3)
c1.metric("Cenário", "Ruptura isolada, dia seco")
c1.caption("N.A. 568,00 m — PAE p. 21, 37, 38")
c2.metric("Trecho modelado", "≈ 33 km")
c2.caption("Da UHE Jurumirim até a barragem da UHE Piraju — PAE p. 37, 52")
c3.metric("Tempo até UHE Piraju", "1 h 59 min")
c3.caption("Seção ST-017/ST-016 — PAE p. 38")
st.markdown(tag("OFICIAL") + "  " + tag("DERIVADO"), unsafe_allow_html=True)

st.subheader("O que a mancha digitalizada mostra")
m = ov["municipios"]
u = ov["urbanizadas"]
us = data.urban_summary()
env_km2 = data.polygons().query("classe=='ENVOLTORIA_RUPTURA'").area_km2.iloc[0]
a, b, c = st.columns(3)
a.metric("Envoltória (ZAS+ZSS)", f"{env_km2:.1f} km²")
a.caption("Derivado da prancha p. 38 (vetorização por cor)")
pm = m[m.municipio == "Piraju"].iloc[0]
b.metric("% do município de Piraju na envoltória", f"{pm.pct_do_municipio:.1f} %")
b.caption(f"{pm.area_envoltoria_no_municipio_km2:.1f} km² de {pm.area_municipio_km2:.0f} km² (IBGE)")
c.metric("Maior mancha urbanizada de Piraju → envoltória", f"{us['main_distance_m']/1000:.1f} km")
c.caption(f"Maior polígono urbanizado IBGE 2019 de Piraju ({us['main_area_km2']:.1f} km²), distância mínima à envoltória")
st.markdown(tag("DERIVADO"), unsafe_allow_html=True)
hit = ", ".join(f"polígono {p['id_poligono']} ({p['densidade'].lower()}, {p['area_km2']:.2f} km², "
                f"{p['area_na_envoltoria_km2']*1e6:,.0f} m² dentro = {p['pct_na_envoltoria']:.1f} %)" for p in us["intersecting_polygons"])
st.info(
    f"Leitura cuidadosa: na digitalização da prancha, o **maior polígono urbanizado do IBGE (2019) de Piraju não intersecta a "
    f"envoltória** (distância mínima ≈ {us['main_distance_m']/1000:.1f} km). **{us['n_intersecting']} polígonos pequenos e pouco densos "
    f"na periferia/ribeirinha intersectam marginalmente**: {hit}. Essas sobreposições são da ordem da incerteza de digitalização "
    "(dezenas de metros). O próprio PAE rotula ST-014 e ST-015 como «Área urbana Pirajú ME» (margem esquerda). "
    "Isto **não** classifica nenhum endereço como seguro ou inseguro."
)

st.subheader("Barragens no dashboard")
import pandas as pd  # noqa: E402
from common import D  # noqa: E402
st.dataframe(pd.DataFrame([dict(Barragem=d.name, Empreendedor=d.owner, Documento=d.document,
                                Seções="sim" if d.has_sections else "não (só resumo)",
                                Mancha="digitalizada (p. 38)" if d.has_polygon else "indisponível no PDF") for d in D.DAMS.values()]),
             hide_index=True, width="stretch")
st.caption("Use o filtro **Por Barragem Isolada / Todas barragens selecionadas** na barra lateral das demais páginas. "
           "'Todas' sobrepõe cenários ISOLADOS; ruptura em cascata não foi modelada. Veja *Cascata Piraju* e *Simulação*.")

st.subheader("Perguntas científicas")
st.markdown(
    "1. **Quais áreas de Piraju constam na mancha?** → página *Mapa interativo* e tabelas de sobreposição.\n"
    "2. **Tempos, sobrelevações, velocidades e vazões?** → página *Seções da onda*.\n"
    "3. **Relação mancha × relevo × vias?** → *Mapa interativo*.\n"
    "4. **Sensibilidade à digitalização e ao DEM?** → *Método e qualidade*.\n"
    "5. **O que não pode ser inferido?** → ver ressalvas abaixo."
)
st.subheader("Ressalvas essenciais")
st.markdown(
    "- O PAE é um **estudo de emergência**; não é evidência de falha iminente e não informa probabilidade de ruptura.\n"
    "- O cenário é **extremo e hipotético** (ruptura da barragem de concreto, N.A. 568,00 m). Não se extrapola para outras cotas.\n"
    "- A modelagem do PAE **termina na barragem da UHE Piraju**; o que ocorre além disso está fora do estudo.\n"
    "- Reproduzir o mapa do PAE **não valida** um modelo hidráulico independente.\n"
    "- Nenhum resultado aqui avalia imóveis, endereços ou rotas específicos — consulte a **Defesa Civil**."
)
footer("Use o menu lateral para navegar.")
