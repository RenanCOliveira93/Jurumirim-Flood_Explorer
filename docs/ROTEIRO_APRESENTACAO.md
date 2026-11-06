# Roteiro de apresentação — vídeo e slides

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

Base: os três perfis do projeto (👷 engenheiro, 🏠 morador de Piraju, 🌍 pessoa de fora). Perguntas e respostas: [`PERGUNTAS_E_RESPOSTAS.md`](PERGUNTAS_E_RESPOSTAS.md). Documentação: [`DOCUMENTACAO.md`](DOCUMENTACAO.md).

## 0. Regras de ouro (valem para vídeo e slides)
1. **Diga sempre a origem do número:** oficial, derivado, estimativa ou ilustração. Mostre o selo na tela.
2. **Nunca diga** «sua casa está segura/em risco», «a barragem vai romper», «a cascata aconteceria» ou dê probabilidade. O projeto não faz isso.
3. **Cascata:** diga «ninguém estudou»; o encadeamento no tempo é só hipótese de relógios. O **cenário de volume** (simulador ANUGA) **não é cascata**: Paranapanema e Piraju entram como terreno.
4. **Piraju:** o mapa de ruptura não existe nos PDFs; o roxo é **estimativa**.
5. **Duração da inundação:** «não é possível calcular com os documentos disponíveis».
6. Aviso fixo no rodapé de todo slide e quadro: *Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.*
7. Não mostre contatos pessoais dos PAEs. Cite as fontes (slide final).
8. **Cenário de volume:** selo **SIMULAÇÃO EXPLORATÓRIA · CENÁRIO HIPOTÉTICO DE VOLUME** na tela. Fale sempre «**se** este volume chegasse ao vale, **nestas premissas**…». Nunca «a cidade será/não será inundada». Diga que o tempo de esvaziamento (72 h), o ponto de entrada e o relevo de 30 m (sem o leito do rio) são premissas; que não há calibração nem revisão de engenheiro; e que **não prova que a cidade seria poupada**.

## 1. Versões
| Versão | Duração | Público | Foco |
|---|---|---|---|
| **Principal** | 7–8 min (+ ~1 min com o bloco opcional do cenário de volume, §2b) | os três | gancho → resposta para o morador → como sabemos → o que ninguém sabe |
| **Corte simulador** | 2 min | 👷/🌍 | «e se 100 % do volume chegasse ao vale?»: premissa, resultado, limites (§2b) |
| **Corte morador** | 90 s | 🏠 | a cidade, o tempo, o que fazer com a informação |
| **Corte engenheiro** | 3 min | 👷 | método, validação, incertezas, inconsistências |
| **Corte curioso** | 60 s | 🌍 | o que é, por que importa, quão confiável |

## 2. Vídeo principal (7–8 min)
Material de tela: `outputs/drone_orbita_piraju.mp4`, `drone_frente_piraju.mp4`, `drone_frente_jurumirim.mp4`, `docs/img/relevo_*.png`, `docs/img/3d_*.png` e telas do dashboard (`make run`).

| # | Tempo | Perfil | Imagem | Narração (sugestão) | Selo/legenda na tela |
|---|---|---|---|---|---|
| 1 | 0:00–0:25 | 🌍 | voo de reconhecimento (`drone_orbita_piraju`) | «Piraju, no interior de São Paulo, vive ao lado de um rio com três barragens em sequência. Há uma lenda: se Jurumirim rompesse, a cidade inteira seria inundada. Vamos conferir com os planos oficiais.» | ILUSTRAÇÃO · exagero vertical 4× |
| 2 | 0:25–0:55 | 🌍 | slide «Jurumirim → Piraju → Paranapanema» + volumes | «Jurumirim guarda 7 bilhões de metros cúbicos; Piraju, 105 milhões, cerca de 66 vezes menos; Paranapanema, 12 milhões. Cada barragem tem um PAE, o plano que descreve um cenário hipotético de acidente. Não é previsão.» | DADO OFICIAL (PAEs) |
| 3 | 0:55–1:20 | 🌍 | tela «Visão de drone» → guia de cores | «Verde-escuro é o fundo do vale; marrom e branco, os morros. Azul é a água de hoje, laranja é a cidade. A água segue o caminho mais baixo.» | legenda de cores |
| 4 | 1:20–2:30 | 🏠 | `drone_frente_jurumirim` + mapa interativo (Jurumirim) | «Pelo mapa oficial do PAE, a mancha da ruptura de Jurumirim cobre 30 km², mas só 5,3 % do município de Piraju, quase tudo rural e à beira do rio. A maior área urbanizada da cidade fica a 2 km da mancha. Duas áreas pequenas são tocadas: 3 mil metros quadrados, 0,04 % da área urbanizada. A onda levaria 1 hora e 59 minutos para chegar à barragem de Piraju.» | DERIVADO DO PAE · PAE p. 38 |
| 5 | 2:30–3:30 | 🏠 | `drone_frente_piraju` + `relevo_piraju.png` | «E se fosse a barragem de Piraju? O PAE dela não traz o mapa. Então fizemos uma estimativa: preenchemos o terreno até a altura de água que o PAE informa. Resultado: cerca de 11 km², tocando 1 % da área urbanizada. Em 17 minutos a água percorreria 9 km. Isto é uma estimativa, não o mapa oficial.» | ESTIMATIVA EXPLORATÓRIA |
| 6 | 3:30–4:10 | 🏠 | tela «Altitude, força, extensão», aba 2 e 4 | «A água se espalharia, em média, 56 metros além da margem do rio; em 9 de cada 10 pontos, até 161 metros. A cidade tem terreno de 490 a 650 metros; a água da ruptura chegaria a cerca de 517 metros naquela região.» | ESTIMATIVA |
| 7 | 4:10–4:40 | 🏠 | slide «E a minha casa?» | «Este projeto não diz se uma casa ou rua seria atingida. O relevo tem 30 metros de resolução. Procure a Defesa Civil e o PAE. Conheça a sua rota de fuga.» | aviso fixo |
| 8 | 4:40–5:50 | 👷 | notebook 02 (georreferência) + notebook 06 (OCR) | «Como sabemos? O mapa de Jurumirim foi georreferenciado com 36 pontos, erro de 0,47 metro; a vetorização tem erro de poucos metros. As tabelas de Piraju são imagens: lemos por OCR em duas escalas, sem divergência, e com checagens físicas. Ainda não houve revisão por engenheiro.» | DERIVADO DO PAE |
| 9 | 5:50–6:30 | 👷 | gráfico de pressão dinâmica (aba 1) | «A ruptura de Piraju tem pressão dinâmica da água, em mediana, quase 6 vezes a da cheia natural. São valores máximos no canal, não no terreno.» | DERIVADO DO PAE |
| 10 | 6:30–7:10 | 👷/🌍 | tela «Cascata Piraju» (lacunas) | «O que ninguém sabe: o que aconteceria em cascata. Os PAEs adotam ruptura isolada. Também não dá para dizer por quanto tempo a água ficaria: os documentos não trazem a descida do nível.» | `not_modelled` |
| 11 | 7:10–7:40 | 🌍 | slide «Como confiar» + fontes | «Tudo é reprodutível e testado, mais de cem testes, e as falhas que encontramos estão no relatório de validação. As fontes são os PAEs de Jurumirim, Piraju e Paranapanema e o PSB de Piraju.» | referências |
| 12 | 7:40–8:00 | todos | tela final | «Estudo educacional independente. Não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.» | aviso fixo |

## 2b. Bloco opcional: cenário de volume (≈ 1 min 10 s; inserir entre as cenas 10 e 11)
Material de tela: `docs/resultados/jurumirim_7007hm3.mp4` (repositório `simulador-hidro-anuga`), `docs/img/sim_volume_08h.png`, `docs/img/sim_volume_pico.png`, e o 3D interativo (`simulador-visualizar html3d`).

| # | Tempo | Perfil | Imagem | Narração (sugestão) | Selo/legenda na tela |
|---|---|---|---|---|---|
| 10b-1 | 0:00–0:20 | 🌍 | `sim_volume_08h.png` → início do MP4 | «E se, em vez de perguntar como a barragem romperia, assumíssemos que todo o volume de Jurumirim, 7 bilhões de metros cúbicos, chegasse ao vale? Isso não é previsão: é uma premissa. Escolhemos esvaziar em 72 horas e simulamos as primeiras 24, com um programa de código aberto, o ANUGA.» | SIMULAÇÃO EXPLORATÓRIA · CENÁRIO HIPOTÉTICO DE VOLUME |
| 10b-2 | 0:20–0:45 | 🏠 | MP4 (frente da água) → `sim_volume_pico.png` | «Nesse cenário, a água fica no vale do rio. Ela chega à barragem de Piraju em cerca de 5 horas e atinge cerca de 9 % da área urbanizada de Piraju e 14 % da área rural. No vale, a profundidade chega a 54 metros, às 18 horas e meia, e depois deixa de subir.» | resultado condicional a estas premissas |
| 10b-3 | 0:45–1:10 | 👷/🌍 | 3D interativo (girar) → aviso na tela | «Atenção aos limites: Paranapanema e Piraju foram tratadas como terreno, então não é cascata. O relevo tem 30 metros e não enxerga o leito do rio. Nada foi calibrado nem revisado por engenheiro. Isto não prova que a cidade seria poupada; se o volume passa da capacidade das barragens, passar por cima ou romper é esperado, e isso não foi modelado.» | NÃO É PREVISÃO · NÃO É CASCATA |

## 3. Cortes por perfil
**🏠 Morador (90 s):** cenas 1 (10 s), 4, 5 (resumidas), 7. Termine com «procure a Defesa Civil».
**👷 Engenheiro (3 min):** georreferência e vetorização (incertezas), OCR e checagens, resíduo de 1,15–1,37 m não explicado, inconsistências das fontes (vertedouro 2.621 × 2.594 m³/s etc.), estimativa e validação (94,6 % de cobertura; mede cobertura, não excesso), cascata `not_modelled`, duração não calculável, reprodutibilidade (`make`).
**🌍 Curioso (60 s):** cenas 1–3, uma frase sobre a estimativa e o aviso final.
**Simulador (2 min):** bloco 2b completo + uma frase sobre como reproduzir (`simulador-hidrograma` → `simulador-hidro` → `simulador-impacto` → `simulador-visualizar`) + próximos passos (malha fina em Piraju, sensibilidade, balanço de massa, barragens como estruturas) + aviso final.

## 4. Slides (19)
Cada slide: título (mensagem), conteúdo, visual, nota do apresentador. Rodapé fixo com o aviso.

| # | Título (mensagem) | Conteúdo | Visual | Perfil | Nota do apresentador |
|---|---|---|---|---|---|
| 1 | Piraju seria alagada? | pergunta + aviso | `3d_piraju.png` | 🌍 | abra com a pergunta, sem resposta |
| 2 | Três barragens em sequência | Jurumirim 7.007,52 hm³ · Piraju 105,58 · Paranapanema 12,2 | esquema + `relevo_corredor.png` | 🌍 | o tamanho muda tudo |
| 3 | O que é um PAE | plano de emergência, cenário hipotético, **não é previsão** | ícone/diagrama | 🌍 | evitar alarmismo |
| 4 | Como ler as imagens | cores, ▲▼, exagero vertical | `relevo_piraju.png` | 🌍/🏠 | explique o azul/laranja/roxo/vermelho |
| 5 | O que o PAE de Jurumirim mostra | 30,4 km² · 5,3 % do município · 1 h 59 min | mapa interativo | 🏠 | origem: PAE p. 38 |
| 6 | A cidade e a mancha | maior mancha urbana a 2,0 km · 3.326 m² tocados (0,04 %) | `3d_corredor.png` | 🏠 | IBGE 2019 ≠ perímetro legal |
| 7 | E se fosse Piraju? | sem mapa nos PDFs · ZAS 9,68 km · 84 edificações | tela «Cascata Piraju» | 🏠 | oficial × estimativa |
| 8 | Estimativa de Piraju | ≈ 11,5 km² · ≈ 1,0 % da área urbanizada · 17 min a 9 km | `relevo_piraju.png` | 🏠 | rótulo ESTIMATIVA |
| 9 | Até onde a água chegaria | avanço lateral: 56 m (mediana), 161 m (90 %) | gráfico (aba 2) | 🏠 | além da margem normal |
| 10 | Altos e baixos da cidade | 491–653 m · água ≈ 517 m · 3,3 % abaixo | `relevo_piraju.png` | 🏠 | teto, sem conexão |
| 11 | E a minha casa? | o projeto **não** classifica endereços; Defesa Civil/PAE | texto | 🏠 | resolução 30 m |
| 12 | Como sabemos (método) | georreferência 0,47 m · OCR em 2 escalas · estimativa validada (94,6 %) | notebook 02/06 | 👷 | mede cobertura, não excesso |
| 13 | A força da água | pressão dinâmica 5,9× (mediana) · 85 × 29 kPa | gráfico (aba 1) | 👷 | valores no canal |
| 14 | O que ninguém sabe | cascata `not_modelled` · duração não calculável · sem mapa de Piraju | tela «Cascata» | 👷/🌍 | lacunas = próximos passos |
| 15 | E se 100 % do volume saísse? | premissa de volume (7.007,52 hm³, PAE) · esvaziado em 72 h · pico 54.070 m³/s · **não é ruptura nem previsão** | `sim_volume_08h.png` | 👷/🌍 | selo SIMULAÇÃO EXPLORATÓRIA; volume ≠ vazão |
| 16 | O que a simulação mostrou | ≈ 9 % da área urbanizada · ≈ 14 % da rural · pico 54,6 m às 18,5 h · limites | `sim_volume_pico.png` | 👷/🌍 | não é cascata; não prova que a cidade seria poupada |
| 17 | Confiabilidade e limites | 100+ testes (dashboard) · simulador **sem testes e sem calibração** · inconsistências das fontes · OCR sem revisão | `VALIDATION_REPORT.md` | 👷 | cite as falhas encontradas |
| 18 | Sobre o autor | perfil e GitHub | foto | todos | mais detalhes na página «Sobre o autor» |
| 19 | Fontes e próximos passos | PAEs, PSB, IBGE, Copernicus, OSM · pedir Apêndice 9 e hidrograma à CBA/CTG | lista de referências | todos | link do repositório |

## 5. Roteiro de demonstração ao vivo (5 min)
1. `make run` → **Visão de drone** → região «Corredor» (relevo, camadas jur+pir).
2. **3D interativo** → girar sobre Piraju; mostrar o ponto mais alto e o mais baixo.
3. **Mapa interativo** → ligar/desligar «Situação normal» e «estimativa».
4. **Simulação** → «Todas barragens selecionadas» → mostrar o aviso «NÃO é cascata» → ligar «Encadear no tempo» e mostrar o aviso de hipótese.
5. **Perguntas por perfil** → abrir uma pergunta de cada perfil.
6. **Simulador (fora do dashboard)** → abrir o 3D interativo (`output/jurumirim_7007hm3_3d.html`), girar sobre o vale, usar Play/slider; mostrar o MP4. Reforçar o selo e os limites (não é cascata, relevo de 30 m, sem calibração).

## 6. Checklist de produção
- [ ] `make setup && make test` verdes; `make drone` gerou os vídeos.
- [ ] Gravar a tela em 1080p; fonte do navegador ampliada; esconder favoritos pessoais.
- [ ] Selo (DADO OFICIAL/DERIVADO/ESTIMATIVA/ILUSTRAÇÃO) visível em cada cena.
- [ ] Aviso fixo no rodapé; slide final com referências.
- [ ] Revisar a narração para não afirmar risco de imóveis, probabilidade ou cascata.
- [ ] Se usar o bloco 2b: rodar o simulador (≈ 4 min), gerar o 3D/MP4 e conferir que o selo «SIMULAÇÃO EXPLORATÓRIA · CENÁRIO HIPOTÉTICO DE VOLUME» aparece em todas as cenas; não prometer que o resultado vale para outros tempos de esvaziamento.
- [ ] Confirmar com a CBA se o PSB («Sigilo: Interno») pode ser citado em público.
- [ ] Legendar o vídeo (acessibilidade) e testar com alguém sem conhecimento técnico.
