import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, footer, setup, st, tag  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
from jurumirim import terrain3d as T  # noqa: E402

setup("Visão de drone: onde é alto, onde é baixo e por onde a água iria")
st.markdown(tag("DERIVADO") + " " + tag("ESTIMATIVA") + " " + tag("ILUSTRACAO") + "  Relevo real (satélite Copernicus, 30 m) visto de cima e em 3D, como num mapeamento por drone. "
            "O relevo é **exagerado 4× na vertical** para que os morros apareçam. As áreas de água de **Jurumirim** vêm do mapa oficial do PAE; "
            "as de **Piraju** são uma **estimativa exploratória** (não é o mapa do PAE).", unsafe_allow_html=True)

with st.expander("Como ler estas imagens (guia rápido)", expanded=True):
    st.markdown("""
- **Verde-escuro = lugares baixos** (o fundo do vale, perto do rio). **Marrom e branco = lugares altos** (morros).
- **Azul** = água como ela é hoje. **Laranja** = área da cidade (IBGE 2019). **Roxo** = onde a água chegaria em Piraju, segundo a estimativa. **Vermelho** = mancha oficial de Jurumirim.
- A água segue o **caminho mais baixo**: por isso a mancha acompanha o vale do rio e raramente sobe os morros.
- ▲ marca o ponto **mais alto** da imagem e ▼ o **mais baixo**; as linhas finas ligam pontos de mesma altitude (a cada 20 m).
- Não é previsão, não diz se uma casa específica seria atingida e não substitui o PAE nem a Defesa Civil.
""")

regioes = {k: v["label"] for k, v in T.REGIONS.items()}
t1, t2, t3 = st.tabs(["🗺️ Relevo sombreado", "🧊 3D interativo (gire com o mouse)", "🎬 Vídeos de drone"])


@st.cache_data(show_spinner="Gerando o mapa…")
def _png(key, show):
    return T.png_bytes(T.map_figure(key, tuple(show)))


with t1:
    key = st.selectbox("Região", list(regioes), format_func=regioes.get, key="dr_reg")
    opts = {"jur": "Mancha oficial de Jurumirim", "pir": "Piraju: estimativa exploratória (ruptura TR 10.000)"}
    show = st.multiselect("Camadas de água", list(opts), default=["jur", "pir"] if key == "corredor" else ["pir"], format_func=opts.get, key="dr_show")
    st.image(_png(key, tuple(show)), width="stretch")
    st.caption("Fonte do relevo: Copernicus GLO-30 (superfície, inclui vegetação). Jurumirim: PAE p. 38 (vetorizado). Piraju: estimativa a partir das cotas tabeladas no PAE. "
               "Posição das seções de Piraju é ilustrativa.")

with t2:
    key3 = st.selectbox("Região", list(regioes), format_func=regioes.get, key="dr_reg3")
    show3 = st.multiselect("Camadas de água", list(opts), default=["jur", "pir"] if key3 == "corredor" else ["pir"], format_func=opts.get, key="dr_show3")
    with st.spinner("Montando o 3D…"):
        st.plotly_chart(T.plotly_figure(key3, tuple(show3)), width="stretch")
    st.caption("Arraste para girar, role para aproximar, passe o mouse para ver a altitude. Em Piraju a superfície roxa é a cota máxima da água tabelada no PAE; "
               "em Jurumirim o PAE não dá cota, então a mancha é desenhada rente ao terreno.")

VIDEOS = {
    "drone_orbita_piraju.mp4": ("Voo de reconhecimento ao redor de Piraju", "orbita"),
    "drone_frente_piraju.mp4": ("Piraju: a água avançando sobre o terreno (estimativa)", "frente_piraju"),
    "drone_frente_jurumirim.mp4": ("Jurumirim → Piraju: a onda do PAE avançando (1 h 59 min)", "frente_jurumirim"),
}
with t3:
    st.markdown("Os vídeos aparecem aqui quando existem em `outputs/`. O avanço da água no tempo é uma **INTERPOLAÇÃO ILUSTRATIVA** entre os tempos de chegada que o PAE tabela por seção; "
                "não é resultado hidráulico oficial nem uma simulação.")
    for fn, (titulo, cmd) in VIDEOS.items():
        f = Path(__file__).resolve().parents[2] / "outputs" / fn
        st.subheader(titulo)
        if f.exists():
            st.video(f.read_bytes())
        elif st.button(f"Gerar este vídeo agora (alguns minutos)", key=f"gen_{cmd}"):
            with st.spinner("Renderizando quadros 3D e codificando com ffmpeg…"):
                try:
                    if cmd == "orbita":
                        T.export_video(T.orbit_frames("piraju", 72), f)
                    elif cmd == "frente_piraju":
                        T.export_video(T.front_frames("piraju", ("pir",), 80), f)
                    else:
                        T.export_video(T.front_frames("corredor", ("jur",), 80), f)
                    st.rerun()
                except Exception as ex:  # noqa: BLE001 - ffmpeg ausente etc.: mostrar
                    st.error(f"Falha ao gerar: {ex}")
        else:
            st.info("Vídeo ainda não gerado. Use o botão ou `make drone`.")

footer("Relevo: Copernicus GLO-30. Água normal: OSM. Áreas urbanizadas: IBGE 2019. Jurumirim: PAE p. 38. Piraju: estimativa exploratória.")
