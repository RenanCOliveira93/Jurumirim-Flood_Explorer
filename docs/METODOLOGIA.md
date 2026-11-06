# Metodologia

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

## Fase 0 — Auditoria da fonte
`docs/CATALOGO_FONTES.md` lista onde está cada informação. A página **física 38** (não a numeração interna do PAE) é uma prancha A1
(2384×1684 pt, 1:30.000, 01/10/2024). **Tabela = texto vetorial; mapa = raster** (41 faixas de imagem com contornos rasterizados);
a grade UTM (12 linhas) e os traços das seções ST são vetoriais.

## Fase 1 — Tabela de seções
`jurumirim.pae.extract_sections`: palavras do PDF agrupadas por linha (y) a partir de cada âncora `ST-xxx`, ordenadas por x; números BR e hh:mm
convertidos. Dupla checagem: valores comparados visualmente com a prancha renderizada em alta resolução e testes de faixa/monotonicidade/valores conhecidos
(`tests/test_pae.py`). Ausência (`-`, vazão da ST-017) vira `NaN`.

## Fase 2 — Georreferenciamento e vetorização
- **CRS** da prancha: SIRGAS 2000 / UTM 22S (EPSG:31982). Transformação afim pt→UTM ajustada por mínimos quadrados aos **36 cruzamentos da grade**; RMS 0,47 m.
- **Checagem independente:** o ponto central tabelado de cada ST cai a < 1 m do traço da seção desenhado (ST-001 sem traço próprio).
- **Vetorização por cor:** linhas exatas da legenda — ZAS (255,0,0), ZSS (75,230,0), cheia sem ruptura (0,92,230) — segmentadas em HSV;
  esqueleto; ligação de pontas livres a outro componente (≤ 90 px ≈ 320 m) para fechar lacunas causadas por rótulos/ícones; preenchimento do interior;
  contorno → UTM; simplificação 2,5 m. A tabela (sobreposta ao mapa) é excluída.
- **Derivados:** envoltória = ZAS ∪ ZSS; ZSS_APENAS = envoltória − ZAS. Cheia sem ruptura recortada à envoltória + 40 m (ruído de reservatório/hidrografia) — **confiança baixa**.
- **Interseções** sempre em EPSG:31982 (`assert crs.is_projected`).

## Fase 2/3 — Dados públicos
IBGE (malha municipal; áreas urbanizadas 2019), Copernicus GLO-30 (EGM2008), OSM (vias). Ver `DADOS.md`.

## Terreno
Perfis ao longo dos traços das seções (30 m de passo) são **descritivos**. Não se compara cota de terreno com sobrelevação para estender a mancha.

## Timeline
Marcadores nos tempos tabelados (sem interpolação). Modo opcional de interpolação linear em linha reta entre seções é rotulado
*INTERPOLAÇÃO ILUSTRATIVA, não resultado hidráulico oficial* (não segue o talvegue).

## Barragens a jusante e filtro
1. **Fatos** (`dams_facts.py`): cada valor com documento, página impressa/PDF, flag e verificação manual.
2. **Tabelas 9/10 de Piraju:** OCR em duas escalas; parser que falha se o número de campos não bate; checagens (T9 × T10 em imagens distintas, ruptura ≥ cheia natural, monotonicidade, cota − fundo − profundidade).
3. **Posição das seções:** km do PAE sobre o eixo OSM a partir da coordenada oficial de Piraju (ILUSTRAÇÃO), validada com a coordenada oficial da Paranapanema (46 m), a de Jurumirim ST-017 (45 m), a quilometragem OSM × PAE (9,73 × 9,68 km) e o georreferenciamento da Figura 17 (14 pontos, RMS 7,04 m).
4. **Filtro:** «Por Barragem Isolada» mostra uma barragem; «Todas barragens selecionadas» sobrepõe cenários isolados, cada um com relógio próprio. Estados: atingida / não atingida / sem tempo no PAE. Sem extrapolação além do tabelado; o cenário 568,00 m de Jurumirim não é escalado.
5. **Seleção persistente** entre páginas; a página *Simulação* usa a mesma seleção.

## Estimativa exploratória de Piraju e ZAS (`bathtub.py`, `scripts/build_estimates.py`)
1. **ZAS** = trecho de rio com a extensão do PAE (Piraju 9,68 km; Paranapanema 10 km) sobre o eixo OSM; não é área.
2. **Estimativa**: perfil de cota máxima (Tabela 10 = ruptura; Tabela 9 = cheia natural) interpolado linearmente em km; células do DEM (UTM 22S, 30 m) abaixo do perfil, a ≤ 1,5 km do eixo, conectadas ao rio (semente a ≤ 90 m) e **a jusante** do eixo da barragem. Separada em «ZAS» (≤ 9,68 km) e «além da ZAS».
3. **Sobreposição** com municípios e áreas urbanizadas IBGE 2019 usa as mesmas funções de Jurumirim (`gis.py`), mas os resultados são rotulados ESTIMATIVA.
4. **Validação**: estimativa sem ruptura × mancha clara da Figura 17 (georreferência RMS 7,04 m); `estimativa_metricas.json`.
5. **Encadeamento (hipótese)**: `selection.offsets` soma o tempo tabelado de chegada da onda à barragem seguinte; só desloca relógios.
