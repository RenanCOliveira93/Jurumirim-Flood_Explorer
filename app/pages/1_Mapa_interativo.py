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
    st.warning(S.NOT_CASCADE)
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
for cl in ("ZSS_APENAS", "ZAS", "CHEIA_SR"):
    if jur and show[cl]:
        sub = p[p.classe == cl]
        folium.GeoJson(sub[["classe", "descricao", "area_km2", "geometry"]],
                       style_function=lambda f, col=sty[cl], cl=cl: {"color": col, "weight": 1.2,
                                                                      "fillOpacity": 0 if cl == "CHEIA_SR" else .35},
                       tooltip=folium.GeoJsonTooltip(["descricao", "area_km2"], aliases=["Classe", "Área (km²)"])).add_to(m)
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
for dam, sc in sel.with_sections():
    if dam == "JUR":
        continue
    for _, r_ in D.sections(dam, sc).iterrows():
        lo, la = _to4326.transform(r_.x_utm, r_.y_utm)
        folium.CircleMarker([la, lo], radius=4, color="#d62728", fill=True, fill_color="#fff", fill_opacity=1,
                            tooltip=f"{r_.secao} · km {r_.distancia_km:.2f}",
                            popup=folium.Popup(f"<b>{r_.secao}</b> (Piraju)<br>Dist.: {r_.distancia_km:.2f} km<br>Chegada: {r_.t_frente_min:g} min"
                                               f"<br>Vazão máx.: {r_.vazao_pico_m3s:,.0f} m³/s<br><i>PAE Piraju p. 62 (impr.). Posição "
                                               "ILUSTRATIVA (km ao longo do eixo OSM)</i>", max_width=280)).add_to(m)
folium.LayerControl().add_to(m)
st_folium(m, height=650, use_container_width=True, returned_objects=[])

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

footer("Limites: IBGE (malha municipal e áreas urbanizadas 2019). Vias: © OpenStreetMap (ODbL).")