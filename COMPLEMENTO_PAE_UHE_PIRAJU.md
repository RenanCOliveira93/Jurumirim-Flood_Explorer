# Complemento técnico — PAE da UHE Piraju (CBA)

## Referência documental
- Plano de Ação de Emergência — UHE Piraju, revisão 5, novembro/2025; emissão técnica em 20/10/2025, código 3308-HID-CBA-A-RT-G00-0001.
- PDF público: https://d2biijvbg5ozmx.cloudfront.net/PIRAJU_TARJADO_para_site_76f2c48308.pdf
- Documento de referência a montante: PAE Externo 2026 UHE Jurumirim, CTG Brasil.

## Descobertas verificadas
1. O PAE de Piraju registra articulação dos empreendedores para estudo comum de rompimento em cascata, mas **adota ruptura isolada de Piraju** (seção 5.3.1, p. 58-59).
2. A avaliação hidrológica de Piraju considera a função amortecedora do reservatório de Jurumirim. Cheia natural decamilenar: 4.856 m³/s; amortecida: 2.829 m³/s; redução: 41,7%. Nível calculado: 532,66 m; crista: 534,00 m; borda livre: 1,34 m (p. 44).
3. O PAE registra que o reservatório de Piraju possui capacidade limitada de amortecimento de grandes cheias (p. 44).
4. O estudo de ruptura hipotética de Piraju foi atualizado pela HIDROBR em 2023, com HEC-RAS 6.3.1 e MDT para 35,9 km² a jusante (p. 57).
5. O estudo considera cenários de cheia sem ruptura e ruptura isolada para TR 10 e 10.000 anos; cenários de ruptura adotam cotas iniciais 531,50 m e 532,70 m, respectivamente (p. 59-60).
6. O trecho a jusante da UHE Piraju estudado se estende até a UHE Paranapanema, aproximadamente 9,68 km (p. 63).
7. Apêndices 8 e 9 do PAE identificam memoriais e mapas de inundação; conferir disponibilidade efetiva dos anexos em arquivo separado (p. 81).

## Limites das conclusões
- Não há, no PAE público analisado, demonstração de que a onda de ruptura de Jurumirim necessariamente romperia Piraju, nem garantia de resistência em todos os cenários.
- A vazão de pico da ruptura de Jurumirim não deve ser comparada diretamente com a capacidade nominal do vertedouro como prova de falha. É necessário o **hidrograma completo**, roteamento hidráulico no reservatório de Piraju, condições iniciais e análise estrutural.
- Não sobrepor as manchas de ruptura isolada como se fossem uma simulação integrada em cascata.

## Instruções para Claude Code — extensão do projeto
1. Registrar os dois PAEs em catálogo de fontes, com revisão, data, emissor e URL.
2. Criar seção `Cascata Jurumirim → Piraju → Paranapanema` no dashboard.
3. Exibir comparativo dos cenários **sem ruptura / ruptura isolada Jurumirim / ruptura isolada Piraju**; rotular claramente que **ruptura induzida em cascata não foi simulada**.
4. Extrair e conferir tabelas de vazão, cota, seções, tempos de chegada e mapas; preservar unidades, referências e páginas.
5. Construir diagrama de dependências e painel de lacunas de dados para estudo de cascata.
6. Não produzir cálculo de probabilidade de falha, tempo de ruptura secundária ou mancha de cascata sem modelo validado.
7. Pedir à CBA e à CTG, quando pertinente, a versão pública do estudo conjunto de cascata, memoriais, hidrogramas e arquivos GIS.
8. Distinguir mapa oficial, visualização reconstruída e animação artística em toda interface.

## Pergunta de pesquisa
> Sob quais hipóteses de nível inicial, hidrograma incidente e capacidade hidráulico-estrutural a UHE Piraju poderia ser afetada por uma ruptura hipotética de Jurumirim? Quais resultados são documentados, quais exigem modelagem adicional e quais permanecem indeterminados?

Este complemento é material de pesquisa, não laudo de segurança, previsão de acidente ou orientação de evacuação.
