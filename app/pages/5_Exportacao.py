import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, S, data, footer, setup, sidebar_filter, st  # noqa: E402

from jurumirim import plots, report  # noqa: E402

setup("Exportação")
sel = sidebar_filter()


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150); return b.getvalue()


st.subheader("Seleção atual")
st.caption("Os arquivos seguem o filtro da barra lateral e levam cenário, documento e página de cada valor.")
sec = S.sections_for(sel)
if len(sec):
    meta = sec.assign(source_document=sec.dam.map({d: D.DAMS[d].document for d in D.DAMS}), aviso=(S.CHAIN_BANNER if sel.chain else S.NOT_CASCADE) if sel.is_all else "")
    st.download_button("⬇️ Seções da seleção (CSV)", meta.to_csv(index=False).encode(), "secoes_selecao.csv", "text/csv")
fa = D.facts()
if len(fa):  # dados do PSB (cabeçalho 'Sigilo: Interno') não entram na exportação
    fa = fa[~fa.key.str.startswith("psb_")]
    st.download_button("⬇️ Fatos citados da seleção (CSV)", fa[fa.dam.isin(sel.dam_ids)].to_csv(index=False).encode(),
                       "fatos_selecao.csv", "text/csv")
if "JUR" in sel.dam_ids:
    st.subheader("Jurumirim (arquivos originais)")
    st.download_button("⬇️ Seções (CSV)", data.sections().to_csv(index=False).encode(), "pae_sections.csv", "text/csv")
    p = data.polygons().to_crs(4326)
    st.download_button("⬇️ Manchas (GeoJSON)", p.to_json().encode(), "pae_flood_polygons.geojson", "application/geo+json")
    st.download_button("⬇️ Seções (GeoJSON)", data.section_points().to_crs(4326).to_json().encode(), "pae_sections.geojson", "application/geo+json")
if "JUR" in sel.dam_ids:
    if st.button("Gerar PNGs e relatório"):
        st.session_state["png_map"] = png(plots.overview_map())
        st.session_state["png_sec"] = png(plots.section_charts())
        st.session_state["rep"] = report.build_markdown()
    if "png_map" in st.session_state:
        st.download_button("⬇️ Mapa (PNG)", st.session_state["png_map"], "mapa_visao_geral.png", "image/png")
        st.download_button("⬇️ Gráficos de seções (PNG)", st.session_state["png_sec"], "graficos_secoes.png", "image/png")
        st.download_button("⬇️ Relatório básico (Markdown)", st.session_state["rep"].encode(), "relatorio_basico.md", "text/markdown")
        st.image(st.session_state["png_map"])
footer("Todos os arquivos exportados carregam o aviso e a procedência.")
