import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import footer, setup, st  # noqa: E402

setup("Sobre o autor")
c1, c2 = st.columns([1, 2.2], gap="large")
with c1:
    st.image(str(Path(__file__).resolve().parents[1] / "assets" / "autor.jpg"), caption="Renan Cunha de Oliveira")
    st.markdown("[GitHub](https://github.com/RenanCOliveira93) · [LinkedIn](https://www.linkedin.com/in/renan-oliveira-aiengineer) · "
                "[Nexus Sight](https://www.nexussight.com.br/)")
with c2:
    st.subheader("Engenheiro de IA / Machine Learning")
    st.markdown(
        "Projeto e construo sistemas de IA aplicada, da experimentação e avaliação de modelos até APIs, automação e implantação. "
        "Atuo com **visão computacional**, **agentes de IA e LLMs** (RAG, avaliação, observabilidade), **machine learning** "
        "(classificação, séries temporais) e engenharia em Python, SQL, PyTorch, FastAPI, Docker e nuvem (AWS e Google Cloud). "
        "Sou fundador da **Nexus Sight**, que transforma câmeras de varejo e fluxos de negócio em inteligência operacional.")
    st.info("**Por que este projeto?** Ele une dados geoespaciais, leitura de documentos técnicos (OCR) e comunicação de risco com "
            "honestidade sobre incertezas: o tipo de problema que me interessa (IA geoespacial e sensoriamento remoto). "
            "É um **estudo pessoal e independente**, sem vínculo com os operadores das barragens, e **não substitui** o PAE.")

st.subheader("O que faço além do currículo (projetos públicos no GitHub)")
cards = [
    ("🌱 AgTech", [
        ("AgroGeo-Analytics", "Ciência de dados geoespaciais na cafeicultura de Piraju/SP: NDVI/NDRE do Sentinel-2, talhões, séries temporais e mapas (dados de exemplo sintéticos, rotulados)."),
        ("AgroClimate-Intelligence", "Clima histórico, previsão, satélite e regras de risco explicáveis para talhões, com experimento de ML e backtest."),
        ("Coffee-Big-Data-Intelligence", "Pipeline de dados da cafeicultura paulista (IBGE, NASA POWER, CONAB), com análise honesta dos limites de previsão."),
        ("Terrain-Soil-Intelligence", "Análise de terreno de propriedades: elevação, declividade e solo a partir de DEM Copernicus e SoilGrids."),
        ("AgroFleet-Intelligence", "Telemetria e auditoria de pulverizadores autônomos (dados simulados); sem controle da máquina."),
    ]),
    ("👁️ Visão computacional", [
        ("CattleCount-AI", "Detecção, contagem e rastreamento de bovinos em imagens de drone e vídeo, com API e painel."),
        ("WeedVision-AI", "Detecção de plantas daninhas, exportação ONNX e avaliação de generalização."),
        ("face-detection-mvp", "POC local-first de reconhecimento facial para presença escolar."),
        ("Computer_Vision_Facti_Projects", "Projetos e experimentos de visão computacional."),
    ]),
    ("🛍️ RetailTech", [
        ("Nexus Sight", "Plataforma que usa as câmeras já existentes no varejo para gerar indicadores operacionais (a plataforma é privada)."),
        ("brandpose (fork)", "Exploração de estimativa de olhar de compradores; projeto original de Claudio Escudero."),
    ]),
    ("🤖 LLMs, documentos e automação", [
        ("project_langchain_langgraph_chat", "Aplicação de chatbot com LangChain/LangGraph."),
        ("ocr_medical_requirements", "Exploração de OCR e processamento de documentos."),
        ("mlops-zoomcamp", "Exercícios de MLOps."),
    ]),
]
cols = st.columns(2)
for i, (title, items) in enumerate(cards):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            for name, desc in items:
                st.markdown(f"- **{name}** — {desc}")
st.caption("Parte do trabalho profissional e de clientes é privada ou confidencial; os repositórios públicos são exemplos selecionados. "
           "Sites e páginas web também fazem parte do portfólio (veja o GitHub e a Nexus Sight).")
footer("Texto baseado no currículo e nos READMEs públicos do autor.")
