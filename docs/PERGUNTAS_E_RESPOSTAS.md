# Perguntas e respostas por perfil

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

Todas as respostas usam **apenas** o que o projeto sabe: os PAEs oficiais, o PSB de Piraju, o relevo Copernicus, IBGE e OSM. Cada resposta indica **de onde vem** o dado e **onde ver no dashboard**. Rótulos: **DADO OFICIAL** (valor do PAE) · **DERIVADO DO PAE** (processado) · **ESTIMATIVA EXPLORATÓRIA** (cálculo do projeto) · **ILUSTRAÇÃO**.

Três perfis, 10 perguntas cada: o engenheiro (técnico), o morador de Piraju (curioso sobre a cidade) e a pessoa de fora (interessada no tema).

## 👷 Perfil 1 — Engenheiro

### E1. De onde vêm os dados e como cada fonte foi tratada?
Quatro documentos: PAE Jurumirim (CTG, R0 jan/2026, 72 p.), PAE Piraju (CBA, emissão 20/10/2025, 87 p. com capa), PSB de Piraju (17 p.) e PAE Paranapanema (Enel, rev. 08, 21 p.). Cada um tem SHA-256 registrado em `data/metadata/source_registry.json`. **Numeração:** em Piraju, página do PDF = impressa + 1; em Paranapanema, «PAGE n of 21» = página do PDF. Toda citação traz página impressa e do PDF. O PSB traz «Sigilo: Interno»; seus derivados ficam fora do Git. *Ver:* página «Método e qualidade»; `docs/SOURCE_REGISTRY.md`.

### E2. Como foi feito o georreferenciamento e a vetorização do mapa de Jurumirim, e qual é a incerteza?
Georreferência afim com **36 pontos de controle** (grade UTM vetorial da prancha, p. 38): RMS **0,47 m**, resíduo máx. 0,57 m; 16 de 17 seções conferem a < 1 m do traço próprio. A mancha é raster, vetorizada por cor (esqueleto + ligação de pontas): erro estimado de 1–3 px (≈ 3,5–10 m), mais a incerteza do próprio PAE (escala 1:30.000), não quantificável. Áreas: ZAS 6,83 km², ZSS 23,55 km², envoltória 30,39 km². Não há verdade de terreno vetorial para medir o erro. *Ver:* notebooks 01–02; `docs/METODOLOGIA.md`.

### E3. Como foram extraídas as Tabelas 9 e 10 de Piraju e quão confiáveis são?
São **imagens**, sem texto; foram lidas por OCR (RapidOCR, duas escalas) com parser que falha se o número de campos não bate. As duas escalas concordaram em 100 % das linhas (46 na Tabela 10, 115 na Tabela 9), mas isso mostra estabilidade, não verdade. Checagens físicas: as imagens distintas das Tabelas 9 e 10 coincidem em fundo e distância; a cota máxima da ruptura é ≥ à da cheia natural; distâncias e tempos crescem a jusante. **Resíduo não explicado:** cota − fundo − profundidade chega a 1,15 m (T10) e 1,37 m (T9). **Não houve revisão de engenheiro:** confira os números críticos na p. 62 impressa. *Ver:* notebook 06.

### E4. Há inconsistências nos próprios documentos?
Sim, registradas e **não corrigidas**: vertedouro controlado de Piraju 2.621 × 2.594 m³/s; TR 10.000 de 2.827,20 (Quadro 9) × 2.829 m³/s (Tabela 8 e PSB); Tabela 9, ST-00, TR 10 com cota 532,70 m (> TR 50 = 531,50 e ≠ condição inicial da Tabela 10); ST-22 com vazão marcada por asterisco sem nota; pico não monótono entre ST-09 e ST-10; Paranapanema com área do reservatório 1,71 × 18,24 km² no mesmo quadro e código de revisão .08 × .05. *Ver:* `docs/SOURCE_REGISTRY.md`.

### E5. Como foi estimada a mancha de Piraju e o que a validação mostra?
**ESTIMATIVA EXPLORATÓRIA:** o relevo Copernicus GLO-30 (30 m, MDS) é preenchido até a **cota máxima tabelada no PAE** em cada seção, interpolada ao longo do rio, só em células conectadas ao rio, a jusante da barragem, num corredor de 1,5 km. Resultado (ruptura, TR 10.000): ≈ 11,5 km² (3,4 km² dentro da ZAS de 9,68 km). Validação possível: a mesma técnica para o cenário **sem ruptura** cobre **94,6 %** (99,7 % com tolerância de 36 m) da parte larga da mancha clara da Figura 17 do PAE. Isso mede cobertura, **não excesso**, e **não valida a ruptura** (sem mapa nos PDFs). Limites: MDS com vegetação, erro vertical de metros, posições das seções ilustrativas, referenciais verticais possivelmente diferentes, sem dinâmica da água. *Ver:* página «Mapa interativo»; `src/jurumirim/bathtub.py`.

### E6. Qual a diferença de «força» entre ruptura e cheia natural em Piraju?
Pela velocidade máxima tabelada por seção: a **pressão dinâmica** ½ρv² da ruptura (TR 10.000) é, na mediana das seções, **5,9×** a da cheia natural do mesmo TR (de 1,4× a 23,3×). Máximos: ruptura 13,0 m/s (≈ 85 kPa); cheia natural 7,6 m/s (≈ 29 kPa); Jurumirim 9,5 m/s (≈ 45 kPa). São valores **máximos na seção do canal** (HEC-RAS), não sobre o terreno nem sobre construções; Jurumirim e Piraju vêm de estudos diferentes. *Ver:* página «Altitude, força, extensão e duração», aba 1.

### E7. Por que a duração da inundação não é calculada e o que faltaria?
Os PAEs tabelam **chegada** e **pico**, mas não trazem o hidrograma completo nem a descida do nível (busca nos quatro PDFs: nada além de glossário). Só há um **teto por conservação de massa**: em Piraju (105,58 hm³) a vazão não pode ficar 5.000 m³/s acima da base por mais de ≈ 6 h; em Jurumirim o teto passa de dias e não informa. Faltam o hidrograma de ruptura e as saídas do HEC-RAS dos estudos originais. *Ver:* aba 5 da mesma página.

### E8. O que foi e o que não foi modelado sobre cascata?
**Não foi modelada.** O PAE de Jurumirim cobre ≈ 33 km e termina na barragem de Piraju (ST-017, sem vazão tabelada); o PAE de Piraju registra que os empreendedores estão «em articulação», mas **adota ruptura isolada** (p. 58). O modo «Todas barragens selecionadas» sobrepõe cenários isolados com relógios independentes. A opção «Encadear no tempo» é só uma **hipótese de relógio**: Piraju começa a contar quando a onda de Jurumirim chega (1 h 59 min); não soma vazões nem calcula interação hidráulica. O status do cenário D permanece `not_modelled` (testado). *Ver:* «Cascata Piraju» e «Simulação».

### E9. Piraju resistiria à cheia decamilenar? Qual a borda livre?
O projeto **não afirma resistência nem falha**. Fatos do PAE (p. 44): cheia TR 10.000 natural 4.856 m³/s, amortecida por Jurumirim 2.829 m³/s (−41,7 %); nível calculado 532,66 m; crista 534,00 m; borda livre 1,34 m. O PAE também diz que o reservatório de Piraju não tem volume significativo para amortecer cheias. Não há análise estrutural neste projeto. *Ver:* «Cascata Piraju».

### E10. Como reproduzo tudo e quão testado está?
`make setup && make test && make run`; `make data`, `make dams`, `make estimates`, `make exposure`, `make drone`, `make notebooks`. A suíte automatizada tem mais de 100 testes (parser, CRS, geometria, filtro, encadeamento, exposição, terreno, páginas do dashboard). Não houve teste em navegador real além de `AppTest` e HTTP. *Ver:* `VALIDATION_REPORT.md`.

## 🏠 Perfil 2 — Morador de Piraju

### M1. A cidade de Piraju seria alagada se Jurumirim rompesse?
Pelo **mapa oficial do PAE** (cenário extremo: ruptura em dia seco com o lago cheio), a mancha cobre ≈ 30,4 km², mas **≈ 5,3 %** do município (26,8 de 506 km²), principalmente área rural e ribeirinha. A **maior mancha urbanizada** de Piraju (IBGE 2019) fica a ≈ **2,0 km** da mancha e **não é tocada**. Duas manchas pequenas e pouco densas são tocadas (3.326 m², **0,04 %** da área urbanizada do município); o próprio PAE rotula as seções ST-014/015 como «Área urbana Pirajú ME». **Não é laudo nem previsão**: é o que o estudo oficial mostra para um cenário hipotético. Consulte a Defesa Civil. *Ver:* «Visão geral», «Mapa interativo».

### M2. Em quanto tempo a água chegaria?
No cenário de Jurumirim, **1 h 59 min** até a barragem de Piraju (tempo em que a água sobe ≥ 0,61 m, tabelado no PAE). Se fosse a barragem de **Piraju** que rompesse (cenário do PAE dela, TR 10.000), a onda chegaria a 1 km em **4 min** e a 9 km em **17 min**. *Ver:* «Seções da onda», «Simulação».

### M3. E se a barragem de Piraju rompesse? Quanto da cidade seria atingido?
O PAE de Piraju **não traz o mapa** (está no Apêndice 9, só listado). O que existe: ZAS de **9,68 km** a jusante e **84 edificações** dentro dela (oficial, p. 63). Minha **ESTIMATIVA EXPLORATÓRIA**: a água cobriria ≈ 11,5 km², tocando **≈ 1,0 %** da área urbanizada do município (≈ 0,085 km², 5 de 19 manchas). É uma estimativa do projeto, **não** o mapa do PAE. *Ver:* «Mapa interativo», «Visão de drone».

### M4. Que partes da cidade são mais baixas e mais altas?
Na mancha urbanizada principal, o terreno vai de **491 m** (beira do rio) a **653 m**, com mediana de **583 m**; a água da ruptura de Piraju chegaria a ≈ **517 m** naquela região, e só **3,3 %** do terreno da mancha fica abaixo disso (teto, sem exigir ligação com o rio). Ou seja: o vale baixo junto ao rio é o que importa; a maior parte da cidade fica bem acima. Relevo de satélite (inclui vegetação). *Ver:* «Visão de drone» (marcadores de ponto mais alto/baixo) e «Altitude, força, extensão e duração», aba 4.

### M5. Minha casa ou rua estaria na mancha?
**Este projeto não responde isso e não classifica endereços, imóveis nem rotas.** A resolução do relevo é de 30 m, a mancha oficial tem incerteza de metros a dezenas de metros e as posições de Piraju são ilustrativas (±centenas de m). Procure a **Defesa Civil** e o **PAE** para a sua localização.

### M6. Quanto a água avançaria para os lados do rio?
Medi o avanço **além da margem atual** do rio. Jurumirim (mancha oficial): mediana **145 m**, 90 % dos pontos até **443 m**, máximo **2,3 km** (nos alargamentos do vale). Piraju (estimativa, ruptura TR 10.000): mediana **56 m**, 90 % até **161 m**, máximo **880 m**. *Ver:* «Altitude, força, extensão e duração», aba 2.

### M7. A barragem pode romper? Qual a chance?
**O projeto não estima probabilidade.** O PAE é um plano de emergência e descreve um cenário hipotético; não é evidência de falha iminente. O PSB de Piraju classifica a barragem como **Classe B: risco baixo, dano potencial associado alto**; a Paranapanema também é classe B (risco baixo, dano potencial associado alto). *Ver:* «Método e qualidade».

### M8. O que é a ZAS e o que ela significa para mim?
ZAS é a **Zona de Autossalvamento**: o trecho a jusante onde a onda chegaria tão rápido que o alerta à população é responsabilidade do empreendedor (definição resumida; confira o glossário de cada PAE). Nos PAEs: Piraju **9,68 km**, Paranapanema **10 km**, Jurumirim mancha de ≈ 6,8 km². O PAE de Piraju diz que a **ZSS** (zona de segurança secundária) **não está definida**. Quem mora na ZAS deve conhecer as rotas de fuga e pontos de encontro do PAE e a Defesa Civil.

### M9. Qual a diferença entre o rio normal e o rio numa ruptura?
A **cota máxima** da água na ruptura de Piraju (TR 10.000) fica, na maior parte do trecho, **de 11 a 14 m acima** da cota máxima da cheia natural do mesmo TR (máximo de 16,6 m), e a **pressão dinâmica** é, na mediana, **5,9×** a da cheia natural. A camada azul «situação normal» do mapa mostra o rio e os lagos como são hoje, para comparar. *Ver:* «Mapa interativo» (círculos coloridos), «Altitude, força, extensão e duração».

### M10. Isso é uma previsão? Posso usar para decidir algo sobre minha casa?
**Não.** É um estudo educacional independente que reaproveita mapas e tabelas oficiais e acrescenta uma estimativa claramente rotulada. Não substitui o PAE, a Defesa Civil nem laudo de engenharia. Para segurança pessoal, use as orientações oficiais.

## 🌍 Perfil 3 — Pessoa de fora, curiosa

### O1. O que é um PAE?
**Plano de Ação de Emergência**: documento que o dono de uma barragem prepara para o caso de um acidente. Descreve um cenário hipotético de ruptura, mapas da área atingida, tempos de chegada e como alertar a população. **Não é uma previsão** nem diz que a barragem está em risco.

### O2. O que este projeto mostra, em uma frase?
Ele reúne os planos oficiais das barragens de Jurumirim, Piraju e Paranapanema e mostra, em mapas, 3D e vídeos, **por onde a água iria num cenário extremo hipotético**, o que é oficial e o que é estimativa, e o que ninguém sabe ainda.

### O3. Por que três barragens?
Elas ficam em sequência no **Rio Paranapanema**, de montante a jusante: **Jurumirim**, **Piraju** e **Paranapanema**. A lenda local diz que um rompimento em Jurumirim inundaria toda Piraju; o projeto confere isso com o mapa do PAE.

### O4. Qual é o tamanho de cada uma?
Pelos volumes dos PAEs: Jurumirim guarda **7.007,52 hm³** no nível máximo normal; Piraju **105,58 hm³** (≈ **66×** menos); Paranapanema ≈ **12,2 hm³** (≈ **574×** menos que Jurumirim). Piraju tem 36 m de altura e crista a 534,00 m.

### O5. Se uma barragem rompesse, a água derrubaria as outras?
**Ninguém estudou isso**, e o projeto também não. Os PAEs adotam **ruptura isolada**; o de Piraju diz que os empreendedores estão «em articulação» para um estudo conjunto. O projeto mostra os cenários isolados lado a lado, e há uma opção opcional que apenas **desloca os relógios** (Piraju começaria a 1 h 59 min), sem somar vazões. Isso é uma hipótese ilustrativa, não um resultado.

### O6. Como foi feito sem rodar uma simulação?
Reaproveitando o que já é oficial: o **mapa** do PAE de Jurumirim (convertido para dados), as **tabelas** de tempos, velocidades e cotas, e o **relevo de satélite** para as imagens em 3D. Para Piraju, que não tem mapa nos PDFs, há uma **estimativa** que preenche o terreno até a cota que o PAE informa; ela é validada contra uma figura do próprio PAE e vem sempre rotulada.

### O7. Quão confiável é?
Depende da parte. **Oficial:** mapa e tabelas do PAE de Jurumirim (convertidos com erro de metros a dezenas de metros). **Leitura por OCR:** tabelas de Piraju, sem revisão de engenheiro. **Estimativa:** mancha de Piraju (não é o mapa do PAE). O painel «Método e qualidade» e o relatório de validação mostram os testes e as falhas encontradas.

### O8. O que são esses mapas coloridos de relevo?
Verde-escuro é o fundo do vale e o marrom/branco são os morros; o relevo é **exagerado 4×** para aparecer. A água segue o caminho mais baixo, por isso a mancha acompanha o rio. ▲ marca o ponto mais alto e ▼ o mais baixo de cada imagem. *Ver:* «Visão de drone».

### O9. Posso usar o projeto para outra cidade?
O código é livre (GPL-3.0). Para outra barragem é preciso um PAE com mapa georreferenciável e tabela de seções; o pipeline de extração, vetorização, relevo e dashboard é reaproveitável, mas cada documento exige conferência humana.

### O10. Onde ficam as fontes?
Na seção de referências de `docs/DOCUMENTACAO.md` e em `docs/SOURCE_REGISTRY.md`: PAE Jurumirim (CTG), PAE e PSB de Piraju (CBA), PAE Paranapanema (Enel), além de IBGE, Copernicus GLO-30 e OpenStreetMap.
