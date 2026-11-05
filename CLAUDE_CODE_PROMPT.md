# PROMPT PARA CLAUDE CODE — JURUMIRIM FLOOD RISK EXPLORER

Você é um time formado por geospatial engineer, especialista em SIG, engenheiro de software Python, analista hidrológico/hidráulico e redator de documentação científica. Desenvolva um MVP técnico local para macOS, separado de qualquer projeto AgTech ou da Nexus Sight.

## Contexto e fonte obrigatória
O usuário mora em Piraju-SP e quer investigar a lenda de que uma ruptura da barragem de Jurumirim inundaria toda a cidade. A fonte primária é o arquivo `CTG-SB-PAEE-2026-R0-JUR.pdf` (PAE Externo UHE Jurumirim, janeiro/2026, 72 páginas). Leia integralmente as seções relevantes, principalmente páginas físicas 21, 37, 38, 52, 54 e 55. A página 38 é uma prancha grande com mapa e tabela; examine-a visualmente em alta resolução. Não confunda a numeração interna do PAE com a página física do PDF. Leia `docs/CONCEITO_E_PLANO.md` antes de começar. Há imagens e textos extraídos em `study/`, mas o PDF original é a fonte autoritativa.

## Objetivo
Construir aplicativo interativo **local**, cientificamente honesto, que permita verificar quais áreas de Piraju constam na mancha oficial de inundação e explorar seções, tempos de chegada e parâmetros da onda fornecidos pelo PAE. Incluir relevo, perfis altimétricos, comparações espaciais e apresentação visual. Não simular uma ruptura física independente no MVP, não instalar HEC-RAS, não exigir Windows/VM, não usar nuvem paga.

## Stack
Python 3.11+, Streamlit, PyMuPDF, pandas, GeoPandas, Shapely, PyProj, Rasterio, NumPy, Plotly, PyDeck ou Folium, pytest. Dependências e ambiente compatíveis com Apple Silicon/macOS; considerar alternativas se pacote GIS falhar. `requirements.txt` ou `pyproject.toml`, scripts de setup e Makefile. Dados públicos de elevação e limites administrativos devem ser adquiridos por scripts reproduzíveis com links oficiais, data de download, licença e datum. Nunca incluir dados ou credenciais de terceiros sem permissão.

## Fases mandatórias

### Fase 0: auditoria da fonte
- Verifique as páginas 21, 37, 38, 52, 54 e 55 e registre um catálogo com localização de cada informação.
- Leia a prancha de página 38 em alta resolução; identifique legenda, sistema de coordenadas, limites das manchas de ruptura e de cheia sem ruptura, seções ST-xxx, valores e unidades.
- Determine se a prancha é vetorial ou raster; prefira extração vetorial fiel quando possível. Se georreferenciar uma imagem, use pontos de controle verificáveis e registre erro RMS.
- Se uma informação estiver ilegível, marque como pendente; nunca adivinhe.

### Fase 1: dataset de referência
- Extraia a tabela de seções ST-xxx para `data/processed/pae_sections.csv`, incluindo ID, distância, coordenadas, sobrelevação, velocidade, tempo de chegada, vazão de pico, unidade e página-fonte, apenas quando verificáveis.
- Faça dupla checagem da tabela com a imagem; crie `data/metadata/pae_provenance.json` e testes de valores/ranges.
- Gere um notebook `01_pae_extraction.ipynb` explicando como foi feito.

### Fase 2: georreferenciamento e SIG
- Extraia a mancha oficial da página 38 para GeoJSON/GeoPackage com procedência explícita. Se a prancha não permitir separação confiável das manchas, não invente polígonos; apresente o mapa original georreferenciado e documente a limitação.
- Integre limites IBGE, vias OSM e DEM público (Topodata ou Copernicus), registrando resolução, datum horizontal/vertical e precisão.
- Calcule interseções apenas em CRS projetado apropriado. Diferencie município de Piraju, área urbana e regiões ribeirinhas.
- Gere perfis de terreno, mas não use simples comparação de cotas para inferir extensão de ruptura.

### Fase 3: dashboard
Páginas Streamlit:
1. Visão geral: perguntas científicas, cenário oficial, ressalvas.
2. Mapa interativo: manchas, limite municipal, área urbana, relevo, pontos/seções.
3. Seções da onda: distância, tempo, velocidade, sobrelevação, vazão e gráficos.
4. Comparação: ruptura hipotética x cheia sem ruptura, exclusivamente no nível de detalhe fornecido pelo PAE.
5. Método e qualidade: origem, erros de georreferenciamento, fontes, incertezas e limitações.
6. Exportação: PNG, CSV, GeoJSON e relatório básico.
Cada número no dashboard deve ter link ou referência ao documento/página.

### Fase 4: timeline e vídeo
- Crie animação técnica baseada em seções e tempos efetivamente documentados. Se usar interpolação, destaque visualmente 'interpolação ilustrativa, não resultado hidráulico oficial'.
- Crie opção de exportar sequência de quadros ou MP4 por matplotlib/Plotly/FFmpeg, sem GenAI obrigatório.
- Opcionalmente, produza storyboard e prompts para Kling/Seedance, a partir dos mapas reais, sempre com tarja 'Representação artística de cenário hipotético; não é simulação hidráulica'. Não invente profundidade, velocidade ou inundação de ruas específicas.

### Fase 5: documentação e testes
- README.md PT-BR, README.en.md, docs de metodologia, dados, limitações, licenças, validação e guia de execução macOS.
- Notebooks didáticos: extração PAE, CRS e georreferenciamento, DEM e perfis, análise de interseção, tempo de chegada e avaliação de incerteza.
- Testes: parser, unidades, conversão hh:mm, CRS, geometria válida, provenance, cálculo de áreas, comportamento com dados faltantes, smoke test do app.
- Relatório `VALIDATION_REPORT.md` com comandos realmente executados, resultados, falhas e pendências.

## Restrições científicas e de segurança
O PAE é um estudo oficial de emergência, não uma evidência de falha iminente. A reprodução de seu mapa não valida modelo hidráulico independente. Não estime probabilidade de rompimento, não extrapole o cenário de nível 568,00 m para cotas arbitrárias, não infira segurança de imóveis/rotas e não divulgue vídeo ilustrativo como previsão real. Não use IA generativa para determinar a mancha. Incluir em todas as visualizações um aviso: 'Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia'. Não reproduzir contatos pessoais do PAE na interface.

## Fluxo de execução
Comece lendo a documentação, auditando a prancha e propondo um plano curto. Em seguida implemente as fases progressivamente, sem parar na etapa de planejamento. Ao final de cada fase relate arquivos alterados, testes realizados, resultados e bloqueios. Se faltar o PDF original, interrompa a extração e peça o arquivo; nunca finja ter consultado o documento. Se a extração do mapa não for tecnicamente confiável, entregue uma versão com overlay da prancha original e deixe a vetorização marcada como pendente.

## Definition of done
`make setup`, `make run` e `make test` funcionam no macOS; mapa oficial acessível no navegador; tabela de seções conferida; gráficos reprodutíveis; fontes rastreáveis; limites claros; resultados científicos separados de visualizações artísticas; documentação PT/EN; sem APIs pagas nem VM.
