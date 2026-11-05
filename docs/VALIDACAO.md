# Validação

Ver [`VALIDATION_REPORT.md`](../VALIDATION_REPORT.md) para os comandos executados. Resumo das estratégias:
1. Tabela de seções: extração programática × inspeção visual da prancha × Figura 12 (p. 55).
2. Georreferenciamento: RMS nos 36 pontos de controle + checagem independente (ponto central × traço da seção).
3. Geometria: validade, CRS projetado, coerência de áreas (envoltória = ZAS + ZSS_APENAS), seções sobre a mancha (≤150 m).
4. Interseções: casos sintéticos com resposta analítica, sem sobreposição, CRS geográfico (deve falhar).
5. Sensibilidade: buffer de ±d m na envoltória (notebook 05) e agregação do DEM (notebook 03).
6. App: `streamlit.testing.AppTest` em todas as páginas + HTTP 200.
**Não** há validação física/hidráulica: isso exigiria modelo independente (terreno, batimetria, condições de contorno, parâmetros de brecha).
