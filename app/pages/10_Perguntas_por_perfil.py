import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import footer, setup, st  # noqa: E402

setup("Perguntas e respostas por perfil")
md = (Path(__file__).resolve().parents[2] / "docs" / "PERGUNTAS_E_RESPOSTAS.md").read_text(encoding="utf-8")
st.markdown("Escolha o perfil mais parecido com você. Cada resposta diz **de onde vem o dado** e **onde ver no dashboard**. "
            "Rótulos: DADO OFICIAL · DERIVADO DO PAE · ESTIMATIVA EXPLORATÓRIA · ILUSTRAÇÃO.")
blocks = re.split(r"\n## ", md)[1:]
tabs = st.tabs([b.split("\n", 1)[0].strip() for b in blocks])
for tab, b in zip(tabs, blocks):
    with tab:
        for q in re.split(r"\n### ", "\n" + b.split("\n", 1)[1])[1:]:
            title, _, body = q.partition("\n")
            with st.expander(title.strip()):
                st.markdown(body.strip())
footer("Fonte do texto: docs/PERGUNTAS_E_RESPOSTAS.md (também no GitHub).")
