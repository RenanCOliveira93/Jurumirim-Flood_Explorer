import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, data, footer, setup, sidebar_filter, st, tag  # noqa: E402

import folium  # noqa: E402
import numpy as np  # noqa: E402
from pyproj import Transformer  # noqa: E402
from streamlit_folium import st_folium  # noqa: E402

setup("Mapa interativo")
sel = sidebar_filter()
jur = "JUR" in sel.dam_ids
if sel.is_all:
    st.warning(S.CHAIN_BANNER if sel.chain else S.NOT_CASCADE)
if jur:
    st.markdown(tag("DERIVADO") + "  Manchas vetorizadas da prancha p. 38 (Jurumirim). Posição com incerteza (ver *Método e qualidade*).",
                unsafe_allow_html=True)

p = data.polygons().to_crs(4326)
pts = data.section_points().to_crs(4326)
mun = data.municipios().to_crs(4326)
urb = data.urbanizadas().to_crs(4326)
roads = data.roads().to_crs(4326)

with st.sidebar:
    base = st.radio("Mapa base", ["Satélite (Esri)", "OpenStreetMap"])
    show = {
        "ZAS": st.checkbox("ZAS implantada", True),
        "ZSS_APENAS": st.checkbox("ZSS", True),
        "CHEIA_SR": st.checkbox("Cheia TR 10.000 sem ruptura (baixa confiança)", False),
        "zas_trecho": st.checkbox("ZAS — trecho oficial (Piraju 9,68 km · Paranapanema 10 km)", True),
        "estim": st.checkbox("Piraju: estimativa exploratória da mancha (ruptura)", True),
        "estim_nat": st.checkbox("Piraju: estimativa da cheia natural, sem ruptura", False),
        "normal": st.checkbox("Situação normal (água atual, OSM) — comparação", True),
        "rise": st.checkbox("Piraju: elevação da ruptura sobre a cheia natural (por seção)", True),
        "mun": st.checkbox("Limites municipais (IBGE)", True),
        "urb": st.checkbox("Áreas urbanizadas (IBGE 2019)", True),
        "roads": st.checkbox("Vias principais (OSM)", False),
        "secoes": st.checkbox("Seções ST", True),
    }
TO_WGS = Transformer.from_crs(31982, 4326, always_xy=True)
if jur:
    cx, cy = p.geometry.union_all().centroid.x, p.geometry.union_all().centroid.y
else:  # centro das barragens selecionadas (UTM -> WGS84)
    dp = D.dam_points().set_index("dam").loc[sel.dam_ids]
    cx, cy = TO_WGS.transform(dp.x_utm.mean(), dp.y_utm.mean())
m = folium.Map(location=[cy, cx], zoom_start=11, tiles=None, control_scale=True)
if base.startswith("Sat"):
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                     attr="Esri, Maxar, Earthstar Geographics", name="Satélite").add_to(m)
else:
    folium.TileLayer("OpenStreetMap", name="OSM").add_to(m)
sty = {"ZAS": "#d62728", "ZSS_APENAS": "#4be600", "CHEIA_SR": "#005ce6"}
if show["normal"]:
    wat = data.water().to_crs(4326)
    folium.GeoJson(wat[["nome", "geometry"]].fillna(""), name="Situação normal (OSM)",
                   style_function=lambda f: {"color": "#00b8ff", "weight": 1, "fillColor": "#00b8ff", "fillOpacity": .45},
                   tooltip=folium.GeoJsonTooltip(["nome"], aliases=["Água em condição normal"])).add_to(m)
for cl in ("ZSS_APENAS", "ZAS", "CHEIA_SR"):
    if jur and show[cl]:
        sub = p[p.classe == cl]
        folium.GeoJson(sub[["classe", "descricao", "area_km2", "geometry"]],
                       style_function=lambda f, col=sty[cl], cl=cl: {"color": col, "weight": 1.2,
                                                                      "fillOpacity": 0 if cl == "CHEIA_SR" else .35},
                       tooltip=folium.GeoJsonTooltip(["descricao", "area_km2"], aliases=["Classe", "Área (km²)"])).add_to(m)
_PIR_TR = 10000 if "10000" in (sel.scenario("PIR") or "ruptura_tr10000") else 10
if show["zas_trecho"]:
    for dam in [d for d in sel.dam_ids if d != "JUR"]:
        z = D.zas_stretch(dam)
        if z is not None:
            folium.GeoJson(z.to_crs(4326)[["dam", "zas_km_oficial", "nota", "geometry"]], name=f"ZAS {dam}",
                           style_function=lambda f, c=D.COLORS[dam]: {"color": "#d62728", "weight": 7, "opacity": .85},
                           tooltip=folium.GeoJsonTooltip(["zas_km_oficial", "nota"], aliases=["ZAS oficial (km)", "Observação"])).add_to(m)
if "PIR" in sel.dam_ids:
    for tipo, flag, cores, rot in (("natural", "estim_nat", ("#1565c0", "#90caf9"), "cheia natural (sem ruptura)"),
                                   ("ruptura", "estim", ("#8e24aa", "#ce93d8"), "ruptura")):
        if show[flag]:
            ep = D.estimate_polygons(tipo, _PIR_TR)
            if ep is not None and len(ep):
                folium.GeoJson(ep.to_crs(4326)[["classe", "area_km2", "geometry"]], name=f"Estimativa Piraju — {rot}",
                               style_function=lambda f, c=cores: {"color": c[0], "weight": 1, "dashArray": "5",
                                                                  "fillColor": c[0] if f["properties"]["classe"] == "ZAS" else c[1],
                                                                  "fillOpacity": .45 if f["properties"]["classe"] == "ZAS" else .30},
                               tooltip=folium.GeoJsonTooltip(["classe", "area_km2"], aliases=[f"ESTIMATIVA {rot} (ZAS = até 9,68 km)", "Área (km²)"])).add_to(m)
if show["mun"]:
    mun_sel = mun[mun.nome.isin(["Piraju", "Cerqueira César", "Manduri", "Sarutaiá", "Bernardino de Campos"])]
    folium.GeoJson(mun_sel[["nome", "geometry"]], style_function=lambda f: {"color": "#ffffff", "weight": 1.5, "dashArray": "6", "fillOpacity": 0},
                   tooltip=folium.GeoJsonTooltip(["nome"], aliases=["Município"])).add_to(m)
if show["urb"]:
    folium.GeoJson(urb[["Tipo", "Densidade", "geometry"]], style_function=lambda f: {"color": "#ff9800", "weight": .5, "fillOpacity": .5},
                   tooltip=folium.GeoJsonTooltip(["Tipo", "Densidade"])).add_to(m)
if show["roads"]:
    folium.GeoJson(roads[roads.highway.isin(["motorway", "trunk", "primary", "secondary"])][["ref", "highway", "geometry"]],
                   style_function=lambda f: {"color": "#ffeb3b", "weight": 1.5},
                   tooltip=folium.GeoJsonTooltip(["ref", "highway"])).add_to(m)
if jur and show["secoes"]:
    for _, r in pts.iterrows():
        folium.CircleMarker([r.geometry.y, r.geometry.x], radius=5, color="#000", fill=True, fill_color="#fff", fill_opacity=1,
                            tooltip=f"{r.id} — {r.descricao}",
                            popup=folium.Popup(
                                f"<b>{r.id}</b> {r.descricao}<br>Dist.: {r.distancia_km:.2f} km<br>Chegada: {r.tempo_chegada_hhmm}"
                                f"<br>Sobrelev.: {r.sobrelevacao_m:.2f} m<br>Vel.: {r.velocidade_ms:.2f} m/s<br>"
                                f"Vazão: {r.vazao_pico_m3s if r.vazao_pico_m3s == r.vazao_pico_m3s else 'n/d'} m³/s<br>"
                                "<i>PAE p. 38</i>", max_width=260)).add_to(m)
_to4326 = TO_WGS
for dam in sel.dam_ids:
    r_ = D.dam_points().set_index("dam").loc[dam]
    lo, la = _to4326.transform(r_.x_utm, r_.y_utm)
    folium.Marker([la, lo], tooltip=f"{r_.nome}", popup=folium.Popup(f"<b>{r_.nome}</b><br>Posição oficial: {r_.origem}", max_width=300),
                  icon=folium.Icon(color={"JUR": "blue", "PIR": "red", "PAR": "green"}[dam], icon="tint")).add_to(m)
import branca.colormap as cm  # noqa: E402
RISE = cm.LinearColormap(["#ffffb2", "#fd8d3c", "#bd0026"], vmin=0, vmax=18,
                         caption="Piraju: cota máx. da ruptura − cota máx. da cheia natural, mesmo TR (m)")
legend_rise = False
for dam, sc in sel.with_sections():
    if dam == "JUR":
        continue
    tr = 10000 if "10000" in (sc or "") else 10
    cmp_ = D.compare_piraju(tr).set_index("secao") if dam == "PIR" else None
    for _, r_ in D.sections(dam, sc).iterrows():
        lo, la = _to4326.transform(r_.x_utm, r_.y_utm)
        dif = cmp_.dif_cota_m.get(r_.secao) if cmp_ is not None else None
        col = RISE(max(0, min(18, dif))) if (show["rise"] and dif == dif and dif is not None) else "#ffffff"
        legend_rise = legend_rise or col != "#ffffff"
        extra = f"<br>Ruptura − cheia natural: <b>{dif:+.2f} m</b> (cota máx.)" if dif is not None and dif == dif else ""
        folium.CircleMarker([la, lo], radius=7, color="#000", weight=1, fill=True, fill_color=col, fill_opacity=1,
                            tooltip=f"{r_.secao} · km {r_.distancia_km:.2f}" + (f" · +{dif:.1f} m" if dif is not None and dif == dif else ""),
                            popup=folium.Popup(f"<b>{r_.secao}</b> (Piraju, TR {tr})<br>Dist.: {r_.distancia_km:.2f} km<br>Chegada: {r_.t_frente_min:g} min"
                                               f"<br>Vazão máx.: {r_.vazao_pico_m3s:,.0f} m³/s<br>Cota máx.: {r_.elev_max_m:.2f} m{extra}"
                                               "<br><i>PAE Piraju p. 61–62 (impr.). Posição ILUSTRATIVA (km ao longo do eixo OSM)</i>",
                                               max_width=300)).add_to(m)
if legend_rise:
    RISE.add_to(m)
folium.LayerControl().add_to(m)
st_folium(m, height=650, use_container_width=True, returned_objects=[])

if "PIR" in sel.dam_ids and (show["estim"] or show["estim_nat"]):
    st.markdown(tag("ESTIMATIVA") + "  **Piraju:** o relevo (Copernicus 30 m) foi preenchido até a **cota máxima tabelada no PAE** em cada seção. "
                "**Não é o mapa do PAE nem simulação hidráulica.** Roxo = ruptura; azul = cheia natural; tom escuro = dentro da ZAS (9,68 km). "
                "Limites: relevo com erro de metros e vegetação; posição das seções ilustrativa; sem dinâmica da água.", unsafe_allow_html=True)
if any(d != "JUR" for d in sel.dam_ids):
    st.info("**Piraju e Paranapanema têm mancha oficial?** Não nos PDFs: o mapa de ruptura de Piraju está no Apêndice 9 (só listado) e os da "
            "Paranapanema nos Anexos 1–2 (sem coordenadas). Por isso: (1) a **ZAS** é mostrada como o **trecho de rio** com a extensão definida "
            "no PAE (Piraju 9,68 km; Paranapanema 10 km), com posição ILUSTRATIVA; (2) para Piraju há uma **estimativa exploratória** de mancha, "
            "separada do dado oficial; (3) **ZSS**: o PAE de Piraju diz que não está definida e o de Paranapanema só define ZAS. "
            "Paranapanema não tem cotas por seção, então **não há estimativa de mancha** para ela (o PAE cita ≈ 3,4 km², só ordem de grandeza).")
notes = S.coverage_notes(sel)
if notes:
    st.info("**Lacunas do mapa** (nada foi desenhado por suposição):\n\n" + "\n\n".join(f"- {n}" for n in notes))
st.caption("Marcadores das barragens: coordenadas citadas nos próprios PAEs. Seções de Piraju: ILUSTRAÇÃO (posição por quilometragem "
           "sobre o eixo OSM do rio, ± centenas de metros; ver *Método e qualidade*).")
if jur:
  st.subheader("Sobreposição da envoltória de Jurumirim (CRS projetado SIRGAS 2000 / UTM 22S)")
  ov = data.overlap_tables()
  st.markdown("**Municípios** " + tag("DERIVADO"), unsafe_allow_html=True)
  st.dataframe(ov["municipios"].round(2), hide_index=True)
  st.markdown("**Áreas urbanizadas IBGE 2019** — principais polígonos " + tag("DERIVADO"), unsafe_allow_html=True)
  st.dataframe(ov["urbanizadas"].head(10).round(2), hide_index=True)
  st.caption("Área urbanizada IBGE 2019 ≠ perímetro urbano legal. Distância 0 = interseção.")

if "PIR" in sel.dam_ids and show["estim"]:
    st.subheader("Piraju: sobreposição da ESTIMATIVA de ruptura (não do PAE)")
    met = D.estimate_metrics().get(f"ruptura_tr{_PIR_TR}", {})
    val = D.estimate_metrics().get("validacao_fig17_natural_tr10000", {})
    if met:
        c1, c2, c3 = st.columns(3)
        c1.metric("Área estimada total", f"{met['area_total_km2']:.1f} km²")
        c2.metric("Dentro da ZAS (≤ 9,68 km)", f"{met['area_zas_km2']:.1f} km²")
        c3.metric("Manchas urbanizadas IBGE tocadas", f"{met['poligonos_urbanizados_intersectados']} ({met['area_urbanizada_intersectada_m2']:,} m²)".replace(",", "."))
    om, ou = D.estimate_overlap("municipios", f"ruptura_tr{_PIR_TR}"), D.estimate_overlap("urbanizadas", f"ruptura_tr{_PIR_TR}")
    st.markdown("**Municípios** " + tag("ESTIMATIVA"), unsafe_allow_html=True)
    st.dataframe(om.round(2), hide_index=True)
    st.markdown("**Áreas urbanizadas IBGE 2019** (interseção ou a < 2 km) " + tag("ESTIMATIVA"), unsafe_allow_html=True)
    st.dataframe(ou.round(2), hide_index=True)
    if val:
        st.caption(f"**Validação possível:** a estimativa do cenário SEM ruptura cobre {100*val['cobertura_da_mancha_clara_sem_tolerancia']:.0f} % "
                   f"({100*val['cobertura_com_tolerancia_36m']:.0f} % com tolerância de 36 m) da parte larga da mancha clara da Figura 17 do PAE. "
                   "Isso mede cobertura, **não excesso**, e não valida o cenário de ruptura, que não tem mapa nos PDFs. "
                   "Área urbanizada IBGE 2019 ≠ perímetro urbano legal; nada aqui classifica endereços ou imóveis.")
footer("Limites: IBGE (malha municipal e áreas urbanizadas 2019). Vias: © OpenStreetMap (ODbL).")