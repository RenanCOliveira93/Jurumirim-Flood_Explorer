# VALIDATION_REPORT

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

Relatório de comandos **realmente executados** (macOS, Darwin 24.6, Apple Silicon; dev em Python 3.11.9; cópia limpa em Python 3.12.11), em 2026-11-04.

## Comandos e resultados
| Comando | Resultado |
|---|---|
| `python3.11 -m venv .venv && pip install …` | OK (pymupdf 2.1, geopandas 1.2.0, rasterio 1.4.4, streamlit 1.66.1…) |
| `.venv/bin/python scripts/fetch_public_data.py` | IBGE, DEM e OSM baixados. **1ª tentativa OSM: HTTP 502** (Overpass); reexecução com mirrors/retry OK |
| `scripts/fetch_public_data.py ibge_urban` | OK (62 polígonos urbanizados na região) |
| `.venv/bin/python scripts/build_dataset.py` | OK — gera CSV/GPKG/GeoJSON, `pae_provenance.json`, tabelas de interseção |
| `make test` / `pytest -v` | 32 passed na 1ª etapa (suíte atual: ver abaixo) |
| `scripts/make_notebooks.py` + `jupyter nbconvert --execute` (5 notebooks) | OK, sem erros (relançado após correção abaixo) |
| `make run` + `curl localhost:8501` | HTTP 200 e `/_stcore/health` = ok (1ª tentativa travou no prompt de e-mail do Streamlit → `.streamlit/config.toml` com `headless=true`) |
| Cópia limpa (`rsync` sem `.venv`) → `make setup` → `make test` | OK em Python 3.12.11: **31 passed** (suíte antes do teste da Fig. 12; teste adicionado depois, rodou no projeto: 32 passed) |
| `animation.export_mp4()` | `outputs/timeline_onda.mp4` (126 quadros, 12 fps, ffmpeg libx264) |

## Verificações científicas
- **Tabela de seções:** 17 seções extraídas do texto vetorial da p. 38; conferidas visualmente com a prancha renderizada e com a **Figura 12 (p. 55)**, que repete os tempos de chegada (17/17 coincidem; teste `test_arrival_times_match_independent_figure12_p55`).
- **Georreferenciamento:** 36 pontos de controle (grade UTM vetorial), RMS = 0,47 m, resíduo máx. 0,57 m. Checagem independente (ponto central ST × traço da seção): 16/17 < 1 m; ST-001 = 112,6 m (sem traço próprio na prancha — fora da checagem).
- **Vetorização:** pontas livres iniciais/pontes/restantes — ZAS 97/69/44, ZSS 412/415/76, cheia 1233/1443/120. Áreas: ZAS 6,83 km², envoltória 30,39 km², ZSS 23,55 km². Inspeção visual do overlay: contornos ZAS/ZSS seguem as linhas da prancha; **não** há verdade de terreno vetorial para calcular erro (a fonte é raster).

## Falhas, correções e erros meus durante o desenvolvimento
1. `gis.municipality_overlap` levantava `KeyError` sem sobreposição — **achado pelo teste de dados faltantes**, corrigido.
2. **Afirmação inicial incorreta:** o dashboard/relatório dizia "nenhum polígono urbanizado intersecta a envoltória". A tabela completa mostrou **2 polígonos pequenos e pouco densos** (3.326 m²) com interseção marginal. Texto corrigido em app, relatório, notebooks, READMEs; textos agora vêm dos dados (`data.urban_summary`) e há teste (`test_urban_summary_facts`).
3. Parser: o `-` da ST-017 (vazão) era descartado por limite de x — corrigido; valor permanece `NaN` (não adivinhado).
4. Primeira vetorização por fechamento morfológico produziu áreas minúsculas (anéis abertos); substituída por esqueleto + ligação de pontas.

## Pendências e limites conhecidos
- **Cheia de projeto sem ruptura:** vetorização de baixa confiança (cor alterada sob a ZAS, confusão com o reservatório); usar só como indicativo.
- Sem verdade de terreno para o erro de vetorização (estimado em 1–3 px ≈ 3,5–10 m).
- Incerteza do próprio PAE (modelo, escala 1:30.000) não quantificável a partir do documento.
- A prancha não permite separar "cheia sem ruptura" de outros elementos azuis com 100 % de certeza; não houve calibração com validação externa.
- `make data` não foi reexecutado na cópia limpa (dados processados já versionados); foi executado no projeto original.
- Vídeo GenAI: **não produzido** (apenas storyboard opcional).
- Repositório Git: **não publicado** (ver mensagem final).
- Não foi feito teste em navegador real além de `AppTest` (smoke) e HTTP 200.

## Extensão: barragens a jusante (Piraju, PSB, Paranapanema) e filtro — 2026-11-05
Documentos reais recebidos e processados (SHA-256 em `data/metadata/source_registry.json`): PAE Piraju (87 pp.), PSB (17 pp.), PAE Paranapanema (21 pp.).

| Comando / verificação | Resultado |
|---|---|
| `pytest -q` (suíte completa, incl. `test_cascade`, `test_dams`, `test_selection`, `test_app`) | **101 passed** (≈16 s) |
| `make notebooks` (6 notebooks, incl. novo `06_barragens_a_jusante`) | OK; nenhuma célula com erro |
| OCR das Tabelas 9/10 (duas escalas) | 46 linhas (T10) e 115 (T9); **0 discordâncias** entre escalas |
| Checagem física: T9 × T10 (imagens distintas) | fundo e distância coincidem; ruptura ≥ cheia natural; distância e tempo de chegada crescentes |
| Cota − fundo − profundidade | resíduo de 0,00 a 1,15 m (T10) e −0,01 a 1,37 m (T9): **não explicado** |
| Posição das seções de Piraju | validada: Paranapanema oficial 46 m; Jurumirim ST-017 45 m; km OSM 9,73 × PAE 9,68; Fig. 17 (14 pts, RMS 7,04 m). Afastamento aos rótulos da Fig. 17: 445–1070 m |
| Filtro: Piraju isolada × com Jurumirim em «Todas» (t = 30 min) | estados idênticos (teste e notebook) |
| MP4 da seleção (`export_selection_mp4`) e servidor Streamlit | gerado; `/_stcore/health` ok |
| Alegações C-01…C-07 do complemento | conferidas manualmente; 2 correções de página, 1 ressalva |

### Atualização: camadas de paridade, estimativa de Piraju e encadeamento (2026-11-05)
| Verificação | Resultado |
|---|---|
| `pytest -q` | **106 passed** (inclui novos testes de encadeamento e da métrica de elevação) |
| AppTest, modo «Todas» + encadeamento (Simulação em t = 150 e Mapa) | sem exceções |
| `scripts/build_estimates.py` | ZAS: Piraju 9,65 km (OSM) × 9,68 oficial; Paranapanema 9,95 × 10. Estimativa de ruptura TR 10.000: 11,5 km² (ZAS 3,4); cheia natural: 8,0 km². **Correção:** o fechamento morfológico da máscara acrescentava ~0,6 % de células com terreno acima da cota (achado pelo teste de consistência do terreno 3D); agora só entram células abaixo da cota, o que reduziu levemente as áreas (11,6→11,5 km²; urbanizada tocada 86.200→85.066 m²; avanço lateral máximo 1,09→0,88 km) |
| Validação da estimativa SEM ruptura × mancha clara da Fig. 17 | cobertura 94,6 % (99,7 % com tolerância de 36 m); **não mede excesso** |
| Segmentação da mancha clara da Fig. 17 | só captura trechos largos; **não** usada como mancha oficial |
| Mapa no navegador | usuário viu o mapa; erro `AttributeError: data.water` era servidor com módulo antigo em memória (reiniciado) |

Limites: a estimativa **não valida a ruptura**; o relevo é MDS; as posições são ilustrativas. Paranapanema não tem estimativa (sem cotas).

### Atualização: altitude, força, extensão lateral, % urbana e tempo
`pytest -q` → **112 passed** (novos: `tests/test_exposure.py`, página 8 no smoke). `make exposure` gera `data/processed/dams/exposure/*.csv`. A busca nos 4 PDFs por duração/permanência/recessão/hidrograma **não encontrou dado de duração** (só definições de glossário): por isso a duração é registrada como não calculável. Falhas durante o desenvolvimento: três testes meus estavam rígidos demais (NaN em ST-22, arredondamento de 1 m); corrigidos nos testes, não nos dados.

### Falhas e correções nesta etapa
- Segmentação por cor da linha amarela da Fig. 17 **falhou** (baixa saturação/ruído); substituída por quilometragem sobre o eixo OSM com validações independentes.
- Testes antigos assumiam «sem PDF = não verificado»; reescritos. Várias correções menores de UI (colisão de variável, nomes de colunas, `use_container_width` → `width="stretch"`, rótulo de tempo do MP4).
- **Erro meu corrigido:** hashes abreviados incorretamente num rascunho do `docs/SOURCE_REGISTRY.md`; refeitos a partir do registro.

### Pendências e limites
- Transcrição por OCR **sem revisão de engenheiro**; conferir na p. 62 impressa.
- Posições das seções de Piraju são ilustrativas (±centenas de m).
- Sem mancha georreferenciada de Piraju (Apêndice 9) nem de Paranapanema (sem coordenadas/tempos).
- Ruptura em cascata: `not_modelled` (testado).
- PSB «Sigilo: Interno»: derivados fora do Git e das exportações; confirmar divulgação com a CBA.
- Inconsistências das fontes registradas, não corrigidas (`docs/SOURCE_REGISTRY.md`).
- Sem teste em navegador real (apenas `AppTest` e HTTP/health).
- **Git:** sem commits; nada enviado ao GitHub.
