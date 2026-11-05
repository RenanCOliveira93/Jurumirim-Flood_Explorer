# Registro de fontes — Jurumirim → Piraju → Paranapanema

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

Conferido com `make piraju` (grava `data/metadata/source_registry.json`; SHA-256 calculado na execução). PDFs de terceiros ficam **fora do Git**.

| ID | Documento | Emissor | Código / edição | Págs. | SHA-256 |
|---|---|---|---|---|---|
| SRC-JUR | PAE Externo UHE Jurumirim | CTG Brasil | CTG-SB-PAEE-2026-R0-JUR, R0, jan/2026 | 72 | `97be8d2f…88c37c42` |
| SRC-PIR | PAE UHE Piraju (versão «tarjada para site») | CBA / Votorantim; HIDROBR (2023); HEAD5 (2025) | 3308-HID-CBA-A-RT-G00-0001; emissão 20/10/2025; capa REV5 nov/2025 | 87 (capa + 86) | `4db99977…9f20a74b` |
| SRC-PSB | PSB UHE Piraju — Sumário Executivo | CBA | PIR-PS-00-RT, rev. 00 | 17 | `7df1b4d9…6fc2d061` |
| SRC-PAR | PAE UHE Paranapanema | Enel Green Power | GRE.OEM.R.88.BR.H.01111.09.003.08, rev. 08, 15/12/2025 | 21 | `a54526f0…0d9d3796` |
| SRC-COMPL | Complemento técnico do projeto | projeto | sem data | — | `1e4133dd…87c17418` |

Hashes completos em `data/metadata/source_registry.json`.

## Numeração de páginas
- **Piraju:** página do PDF = **impressa + 1** (cabeçalho «Páginas: n de 86»). Este projeto cita páginas **impressas**, como o complemento.
- **Paranapanema:** «PAGE n of 21» = página do PDF.
- Cada fato em `dams_facts.py` traz `page_printed` e `page_pdf`.

## Cuidados
- **PSB:** cabeçalho **«Sigilo: Interno»**. Confirmar com a CBA se pode ser divulgado antes de publicar qualquer derivado. Os dados `psb_*` estão no `.gitignore` e **fora das exportações**.
- **Paranapanema:** o PDF contém contatos pessoais; **não foram reproduzidos**.
- **Apêndices 8 e 9 de Piraju** (memoriais e mapas) são apenas *listados*; não estão no PDF. Os mapas da Paranapanema (Anexos 1–2) também não.

## Alegações do complemento (SRC-COMPL), conferidas no PDF
C-01…C-07 foram **conferidas manualmente** contra o PDF (páginas impressas 44, 57–60, 63, 81). Todas coincidem em substância, com duas **correções de página** (C-01: p. 58; C-05: p. 59–60) e uma **ressalva** (C-06: a ZAS termina na Paranapanema em 9,68 km, mas as Tabelas 9/10 seguem até 32,35 km, ST-22). Ver `cascade.CLAIMS`.

## Inconsistências **nas próprias fontes** (registradas, não corrigidas)
| Item | Observação |
|---|---|
| Piraju, vertedouro controlado | 2.621 (p. 11) × 2.594 m³/s (p. 14) |
| Piraju, TR 10.000 | Quadro 9: 2.827,20 × Tabela 8 / PSB: 2.829 m³/s |
| Tabela 9, ST-00, TR 10 | cota 532,70 m (> TR 50 = 531,50 e ≠ condição inicial da Tabela 10 = 531,50) |
| Tabela 10, ST-22 | vazão com asterisco sem nota de rodapé; pico não monótono entre ST-09 e ST-10 |
| Paranapanema, área do reservatório | 1,71 × 18,24 km² (NA normal × máx. maximorum no mesmo quadro) |
| Paranapanema, código | rev. .08 na capa, .05 no corpo |

## Leitura das Tabelas 9 e 10 de Piraju
São **imagens raster** (sem texto). Lidas por OCR (RapidOCR, opcional: `make ocr`) em duas escalas, com checagens físicas e de consistência; JSON bruto versionado em `data/processed/dams/PIR/ocr_raw/`, recortes PNG fora do Git. **Não houve revisão por engenheiro.** Conferir números críticos na p. 62 impressa (Tabela 10).
