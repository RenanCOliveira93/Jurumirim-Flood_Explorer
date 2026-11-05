# Jurumirim Flood Risk Explorer — Conceito e plano de execução

## Propósito
Projeto independente de engenharia geoespacial e análise de risco de inundação para investigar, com transparência metodológica, a hipótese popular de que uma ruptura da UHE Jurumirim inundaria a cidade de Piraju-SP. Não integra o portfólio AgTech nem a Nexus Sight.

## Perguntas de pesquisa
1. Quais áreas do território municipal e da área urbana de Piraju estão dentro da mancha oficial do PAE?
2. Que tempos de chegada, sobrelevações, velocidades e vazões são apresentados nas seções do estudo?
3. Qual é a relação espacial entre a mancha, o relevo, as edificações e a malha viária?
4. Qual é a sensibilidade dos resultados à precisão da digitalização e à resolução dos dados de terreno?
5. O que **não** pode ser inferido sem nova simulação hidráulica, incluindo alterações de nível inicial do reservatório?

## Documento de referência
CTG Brasil, *Plano de Ação de Emergência de Barragem — Externo, UHE Jurumirim*, CTG-SB-PAEE-2026-R0-JUR, janeiro de 2026, 72 páginas. Arquivo original fornecido pelo usuário: `CTG-SB-PAEE-2026-R0-JUR.pdf`.

### Evidências verificadas
- Página 21 (página física do PDF): cotas operacionais, volumes, geometria e características da barragem.
- Página 37: Seção VI descreve estudo de ruptura isolada da barragem principal de concreto em dia seco, aproximadamente 33 km até a UHE Piraju.
- Página 38: prancha de inundação CTG-SB-DE-2415-JUR; compara ruptura em dia seco com N.A. 568,00 m e cheia de projeto sem ruptura. A prancha contém quadro de seções ST-001 etc. com distância, sobrelevação, velocidade, tempo de chegada e vazão de pico. **A prancha precisa de leitura e conferência visual, não apenas extração textual.**
- Página 52: caracterização do vale a jusante e dados cadastrais de ZAS/vizinhança, com levantamento de 2020.
- Página 54: descrição do tempo de chegada da onda e seu uso na gestão de emergência.
- Página 55: Figura 12, tempo de chegada nas seções de interesse.
- O PAE afirma que uma comparação de imagens de 2019 e 2024 não encontrou mudanças relevantes de ocupação na ZAS; isso não substitui a verificação atual de uso do solo.

## Princípio de validade
O PAE é a referência **oficial**; a extração e a visualização são reconstituições derivadas do documento. Comparar a mancha digitalizada com a mesma imagem de origem verifica fidelidade de digitalização, **não** valida uma simulação hidráulica independente. Para validação física independente seriam necessários modelo hidráulico, dados de terreno/batimetria, condições de contorno e parâmetros de ruptura.

## MVP local macOS
Stack sugerida: Python 3.11+, Streamlit, GeoPandas, Shapely, Rasterio, PyProj, Plotly, PyDeck/Folium, PyMuPDF, pandas, NumPy, pytest. Sem HEC-RAS, VM, cloud ou serviços pagos. Preferir Python/Streamlit para a primeira versão, evitando complexidade desnecessária de React/FastAPI.

### Entregas
1. Ingestão do PAE com catálogo de fontes por página.
2. Extração conferida manualmente da tabela de seções da prancha; CSV versionado com provenance, unidades, datum, incertezas e testes.
3. Digitalização **georreferenciada** da mancha de inundação oficial; estimar erro de registro a partir de pontos de controle; guardar GeoJSON/GeoPackage, metadados e procedimento.
4. Integração com MDE público de fonte e datum documentados; relevo 2D/3D, perfis altimétricos e checagem de compatibilidade vertical.
5. Geometrias de município, área urbana e vias, com origem e ano; sobreposição e estimativas de área apenas com projeção adequada.
6. Dashboard com mapa oficial, tabela de seções, gráficos de distância x tempo/sobrelevação/velocidade/vazão, comparação com cheia sem ruptura **somente onde o documento oferece geometria e dados suficientes**.
7. Timeline de onda **apenas nas seções observadas no PAE**. Interpolação espacial/temporal, se implementada, deve ser marcada como estimativa gráfica, nunca como resultado oficial.
8. Exportação de mapas e gráficos; vídeo técnico produzido com matplotlib/Plotly/FFmpeg, preservando a geometria da mancha. Vídeo GenAI opcional, separado e identificado como representação artística.
9. Relatório final: respostas delimitadas às perguntas, incertezas, fontes, limitações e comparação de resultados.

## Critérios de qualidade
- Não afirmar que toda Piraju seria inundada sem evidência espacial.
- Não classificar um endereço como seguro/inseguro com base neste MVP.
- Não transformar percentual de volume útil em volume total sem curva cota-volume.
- Não usar uma cota de reservatório para escalonar linearmente a mancha oficial.
- Não criar profundidade/velocidade por pixel a partir de uma prancha sem dados hidráulicos.
- Não inferir risco atual de ruptura a partir de cenário hipotético do PAE.
- Não publicar vídeo GenAI como simulação científica.
- Usar etiquetas persistentes: 'DADO OFICIAL', 'DERIVADO DO PAE', 'ESTIMATIVA EXPLORATÓRIA', 'ILUSTRAÇÃO'.
- Apresentar aviso: 'Estudo educacional independente. Não substitui o PAE, a Defesa Civil nem avaliação de engenheiro habilitado.'

## Etapas
0. Verificação da prancha, georreferenciamento e viabilidade da extração.
1. Parsing do PAE e tabela ST-xxx conferida.
2. Digitalização/georreferenciamento da mancha e checagem de erro.
3. MDE, limites territoriais e análise espacial.
4. Dashboard local e timeline técnica.
5. Testes, documentação, vídeo opcional e relatório.

## Definição de pronto
App inicializa no macOS, mostra mancha oficial georreferenciada, permite inspecionar as seções, cita página e fonte de cada número, distingue dados de estimativas, gera pelo menos um gráfico reproduzível, passa testes e explicita o que não foi possível inferir.
