# Comparação entre barragens: Jurumirim × Piraju × Paranapanema

> Material de pesquisa. Não é laudo, previsão de acidente nem orientação de evacuação. Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

Todas as ordens de grandeza abaixo vêm dos PAEs, **de estudos distintos, com hipóteses distintas**. Elas descrevem cada estudo; **não permitem concluir** que uma barragem romperia ou resistiria por causa de outra.

## 1. Fatos verificados nos PDFs (páginas impressas)
| Barragem | Fato | Valor | Pág. |
|---|---|---|---|
| Jurumirim | Cenário do PAE | ruptura isolada, dia seco, N.A. 568,00 m (7.007,52 hm³) | 21, 37–38 |
| Jurumirim | Pico na brecha / ST-016 / chegada a Piraju | 42.728 / 19.928 m³/s / 1 h 59 min; ST-017 sem vazão no PAE | 38, 52–55 |
| Piraju | Crista, altura, volume no N.A. normal | 534,00 m; 36 m; 105,58 hm³ | 14 |
| Piraju | Cheia TR 10.000 natural → amortecida por Jurumirim | 4.856 → 2.829 m³/s (−41,7 %); nível 532,66 m; borda livre 1,34 m | 44 |
| Piraju | Brecha de projeto (ruptura isolada) | 179,5 m × 20,5 m, formação em 6 min; N.A. inicial 531,50 (TR 10) / 532,70 m (TR 10.000) | 60 |
| Piraju | Pico em ST-00, ruptura isolada | TR 10: 22.314 m³/s; TR 10.000: 26.857 m³/s (Tabela 10, OCR) | 62 |
| Piraju | ZAS / ZSS / edificações na ZAS | 9,68 km / não definida / 84 | 63 |
| Piraju | Cascata | empreendedores «em articulação»; **o PAE adota ruptura isolada** | 58 |
| Paranapanema | Crista; classe; potência | 506,80 m; B; 31,5 MW | 4–5 |
| Paranapanema | Cenários (pico) | TR 100: 1.652,57; TR 10.000: 2.800; ruptura: 2.420,13 m³/s | 14 |
| Paranapanema | Conclusão do próprio estudo | cheias naturais mais desfavoráveis que a ruptura; mancha ≈ 3,4 km² (ordem de grandeza); ZAS 10 km | 17–18 |

## 2. O que as fontes **não** trazem
- Hidrograma completo de Jurumirim em ST-017 e entrada em Piraju.
- Mancha georreferenciada de Piraju (Apêndice 9 só lista arquivos) e mapas/tempos da Paranapanema.
- Qualquer estudo conjunto de cascata, com ou sem resultado.
- Por isso a **ruptura em cascata permanece `not_modelled`**.

## 3. Cenários no dashboard
| Cenário | Status |
|---|---|
| A. Ruptura isolada de Jurumirim | `documented` (PAE Jurumirim) |
| B. Cheia de projeto sem ruptura (Piraju) | `documented` (PAE Piraju, p. 44) |
| C. Ruptura isolada de Piraju (TR 10 e TR 10.000) | `documented` (Tabelas 9/10; leitura por OCR) |
| C2. Ruptura isolada da Paranapanema | `documented`, sem seções nem mapa |
| D. Cascata | **`not_modelled`** |

## 3.1 O que cada barragem tem no mapa
| Item | Jurumirim | Piraju | Paranapanema |
|---|---|---|---|
| Mancha oficial (ZAS/ZSS) | sim (p. 38, vetorizada) | **não** (Apêndice 9 ausente) | **não** (Anexos sem coordenadas) |
| ZAS | polígono | **trecho de 9,68 km** (ILUSTRAÇÃO) | **trecho de 10 km** (ILUSTRAÇÃO) |
| ZSS | polígono | «não definida» no PAE | não definida no PDF |
| Seções e tempos | sim | sim (OCR) | **não** |
| Estimativa exploratória de mancha | n/a (há mancha oficial) | **sim**, rotulada | **não** (sem cotas) |
| Sobreposição município/urbanizadas | sim | **só da estimativa** | não |

## 4. Filtro «Por Barragem Isolada» × «Todas barragens selecionadas»
«Todas» **sobrepõe cenários isolados**, cada um com o **relógio da própria ruptura** (t = 0 na ruptura daquela barragem). **Não é cascata**: o tempo de Piraju não depende de Jurumirim. Opcionalmente, **«Encadear no tempo»** supõe que cada barragem rompe quando chega a onda da anterior (Jurumirim→Piraju: 1 h 59 min); só desloca relógios, **não soma vazões** e é uma hipótese, não um estudo. O comportamento é coberto por teste. O texto fixo «NÃO é cascata» aparece em todo resultado do modo «Todas».

## 5. Limites de interpretação
- Vazão de pico não é hidrograma; compará-las entre estudos não prova falha nem segurança.
- Condições iniciais diferem (568,00 m em Jurumirim; 531,50/532,70 m em Piraju).
- As posições das seções de Piraju são **ILUSTRAÇÃO** (km sobre o eixo OSM; ±centenas de m).
- Não inferir segurança estrutural de nenhuma barragem; não extrapolar cheia natural para ruptura.

## 6. Proposta de contato com CBA e CTG
Revisar antes de enviar; não incluir contatos pessoais dos PAEs.

> Sou morador de Piraju e desenvolvo um estudo educacional independente sobre os PAEs de Jurumirim, Piraju e Paranapanema. Peço, se possível: (1) os arquivos/mapas de inundação do Apêndice 9 do PAE de Piraju, se puderem ser divulgados; (2) o hidrograma de ruptura de Jurumirim até a barragem de Piraju; (3) informação sobre estudo conjunto de cascata e eventual versão pública; (4) confirmação se o PSB (marcado «Sigilo: Interno») pode ser citado. O estudo não substitui o PAE nem a Defesa Civil.
