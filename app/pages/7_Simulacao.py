import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, data, footer, setup, sidebar_filter, st, tag  # noqa: E402

import folium  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from pyproj import Transformer  # noqa: E402
from streamlit_folium import st_folium  # noqa: E402

from jurumirim import animation, dam_plots  # noqa: E402

setup("Simulação da frente da onda")
sel = sidebar_filter()
st.markdown(
    tag("OFICIAL") + " " + tag("ILUSTRACAO") + "  Reprodução animada dos **tempos de chegada tabelados nos PAEs**. "
    "Não é simulação hidráulica própria: nada além dos valores publicados é calculado.", unsafe_allow_html=True)
if sel.is_all:
    st.warning(S.CHAIN_BANNER if sel.chain else S.NOT_CASCADE)
else:
    st.info(f"Cenário isolado: {D.sel_label(*sel.rows[0])}. O relógio começa na ruptura dessa barragem.")

tmax = S.t_max(sel)
if tmax == 0:
    st.warning("Nenhuma barragem selecionada tem tabela de seções com tempos no PAE. "
               + " ".join(S.coverage_notes(sel)))
    footer()
    st.stop()

c1, c2 = st.columns([3, 1])
t = c1.slider("Tempo desde a ruptura da 1ª barragem (min)" if sel.chain else "Tempo desde a ruptura de cada barragem (min)", 0, tmax, min(30, tmax), 1,
              help=("HIPÓTESE: relógio comum; cada barragem rompe quando chega a onda da anterior." if sel.chain else "Cada cenário tem relógio próprio: t = 0 é a ruptura da PRÓPRIA barragem."))
interp = c2.checkbox("Frente interpolada", False, help=f"{S.INTERP_BANNER}. Interpolação linear entre seções com tempo tabelado; sem extrapolar.")
if interp:
    st.warning(S.INTERP_BANNER + " (estrela). Interpolação linear entre seções; não há dado do PAE entre elas.")
st.markdown(f"**t = {t//60} h {t%60:02d} min**")

if sel.chain:
    off = S.offsets(sel)
    st.markdown("**Início hipotético do relógio de cada barragem** (tempo tabelado de chegada da onda da barragem a montante): "
                + " · ".join(f"{D.DAMS[d].name}: " + ("não tabelado" if o is None else f"{int(o)//60} h {int(o)%60:02d} min") for d, o in off.items()))
summ = S.summary_at(sel, t)
st.dataframe(summ.rename(columns={"barragem": "Barragem", "cenario": "Cenário", "secoes_atingidas": "Seções atingidas",
                                  "ate_km": "Até o km", "ultima_secao": "Última seção", "vazao_pico_ultima_m3s": "Vazão de pico na última (m³/s)"}),
             hide_index=True, width="stretch")
st.caption("'Atingida' = a frente (início da onda) já chegou à seção segundo o PAE. Para Jurumirim, tempo em que a sobrelevação "
           "atinge 0,61 m; para Piraju, 'tempo de chegada da onda de ruptura' (Tabela 10).")

state = S.state_at(sel, t)
left, right = st.columns([1.15, 1])
with left:
    TO = Transformer.from_crs(31982, 4326, always_xy=True)
    pts = D.dam_points().set_index("dam").loc[sel.dam_ids]
    la0, lo0 = zip(*[TO.transform(x, y)[::-1] for x, y in zip(pts.x_utm, pts.y_utm)])
    m = folium.Map(location=[sum(la0) / len(la0), sum(lo0) / len(lo0)], zoom_start=11, tiles="OpenStreetMap", control_scale=True)
    rx, ry = D.river_xy()
    folium.PolyLine([TO.transform(x, y)[::-1] for x, y in zip(rx[::6], ry[::6])], color="#6baed6", weight=2, opacity=.7,
                    tooltip="Eixo do rio (OSM) — contexto, ILUSTRAÇÃO").add_to(m)
    if "JUR" in sel.dam_ids:
        env = data.polygons().to_crs(4326)
        env = env[env.classe == "ENVOLTORIA_RUPTURA"]
        folium.GeoJson(env.__geo_interface__, name="Envoltória de Jurumirim (digitalizada, PAE p.38)",
                       style_function=lambda _: {"color": "#555", "weight": 1, "fillOpacity": .12}).add_to(m)
    for dam in [d for d in sel.dam_ids if d != "JUR"]:
        zz = D.zas_stretch(dam)
        if zz is not None:
            folium.GeoJson(zz.to_crs(4326)[["zas_km_oficial", "geometry"]], style_function=lambda f: {"color": "#d62728", "weight": 6, "opacity": .6},
                           tooltip=folium.GeoJsonTooltip(["zas_km_oficial"], aliases=["ZAS oficial (km), trecho de rio ILUSTRATIVO"])).add_to(m)
    if "PIR" in sel.dam_ids:
        ep = D.estimate_polygons("ruptura", 10000 if "10000" in (sel.scenario("PIR") or "ruptura_tr10000") else 10)
        if ep is not None and len(ep):
            folium.GeoJson(ep.to_crs(4326)[["classe", "geometry"]], style_function=lambda f: {"color": "#8e24aa", "weight": 1, "dashArray": "5",
                           "fillColor": "#8e24aa", "fillOpacity": .25 if f["properties"]["classe"] == "ZAS" else .12},
                           tooltip="ESTIMATIVA EXPLORATÓRIA (relevo até a cota do PAE); não é mapa do PAE").add_to(m)
    col = {"atingida": "#d62728", "não atingida": "#ffffff", "sem tempo no PAE": "#999999", "ainda não rompeu (hipótese)": "#eeeeee"}
    for _, r in state.iterrows():
        la, lo = TO.transform(r.x_utm, r.y_utm)[::-1]
        folium.CircleMarker([la, lo], radius=7 if r.estado == "atingida" else 5, color=D.COLORS[r.dam], weight=2, fill=True,
                            fill_color=col[r.estado], fill_opacity=1,
                            tooltip=f"{D.DAMS[r.dam].name} · {r.secao} · km {r.distancia_km:.2f} · chegada {r.t_frente_min:g} min · {r.estado}"
                            if r.t_frente_min == r.t_frente_min else
                            f"{D.DAMS[r.dam].name} · {r.secao} · km {r.distancia_km:.2f} · sem tempo no PAE").add_to(m)
    for dam in sel.dam_ids:
        r = pts.loc[dam]
        la, lo = TO.transform(r.x_utm, r.y_utm)[::-1]
        folium.Marker([la, lo], tooltip=r.nome, icon=folium.Icon(color={"JUR": "blue", "PIR": "red", "PAR": "green"}[dam], icon="tint")).add_to(m)
    if interp:
        for dam, sc in sel.with_sections():
            g = D.sections(dam, sc).dropna(subset=["x_utm", "t_frente_min"]).sort_values("distancia_km")
            km = S.front_km(g, t)
            if km is not None:
                la, lo = TO.transform(float(np.interp(km, g.distancia_km, g.x_utm)), float(np.interp(km, g.distancia_km, g.y_utm)))[::-1]
                folium.Marker([la, lo], icon=folium.Icon(color="orange", icon="star"),
                              tooltip=f"{S.INTERP_BANNER}: {D.DAMS[dam].name}, km {km:.1f}").add_to(m)
    st_folium(m, height=520, use_container_width=True, returned_objects=[])
    notes = S.coverage_notes(sel)
    if notes:
        st.caption("Lacunas: " + " | ".join(notes))
with right:
    st.plotly_chart(dam_plots.time_distance(S.sections_for(sel), t_min=t, interpolate=interp), width="stretch")

with st.expander("Estado de cada seção neste instante"):
    st.dataframe(state[["label", "secao", "distancia_km", "t_frente_min", "t_pico_min", "estado", "vazao_pico_m3s", "posicao"]].rename(columns={
        "label": "Cenário", "secao": "Seção", "distancia_km": "Dist. (km)", "t_frente_min": "Chegada (min)", "t_pico_min": "Até o pico (min)",
        "estado": "Estado", "vazao_pico_m3s": "Vazão pico (m³/s)", "posicao": "Posição"}), hide_index=True, width="stretch")

st.subheader("Exportar esta seleção")
b1, b2 = st.columns(2)
fig = animation.frame_selection(sel, t, interp)
buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=130)
b1.download_button("⬇️ Quadro atual (PNG)", buf.getvalue(), f"simulacao_t{t:03d}.png", "image/png")
plt.close(fig)
if b2.button("Gerar MP4 da seleção (alguns segundos)"):
    with st.spinner("Renderizando quadros e codificando com ffmpeg…"):
        try:
            out = animation.export_selection_mp4(sel, interpolate=interp)
            st.session_state["sel_mp4"] = out.read_bytes()
        except Exception as ex:  # noqa: BLE001 - ffmpeg ausente ou falha de render: mostrar, não esconder
            st.error(f"Falha ao gerar o vídeo: {ex}")
if "sel_mp4" in st.session_state:
    st.video(st.session_state["sel_mp4"])
    st.download_button("⬇️ Vídeo (MP4)", st.session_state["sel_mp4"], "timeline_selecao.mp4", "video/mp4")
footer("Tempos: PAEs de Jurumirim (p. 38) e Piraju (Tabela 10). Posições de Piraju: ILUSTRAÇÃO. Não é previsão.")
