# Jurumirim Flood Risk Explorer

Dashboard e pipeline reproduzível em Python que analisam os cenários de ruptura hipotética da barragem de Jurumirim (SP) publicados nos Planos de Ação de Emergência (PAEs) oficiais e seu efeito sobre o município de Piraju.

> Os resultados são cenários condicionais derivados de documentos oficiais e estimativas exploratórias rotuladas. **Não são previsão de ruptura**, não avaliam a segurança de barragens, imóveis, endereços ou rotas, e não substituem o PAE oficial, a Defesa Civil ou laudo de engenharia. O projeto não executa simulação hidráulica própria; reproduzir o mapa do PAE não valida um modelo independente.

English: [README.en.md](README.en.md)

## Funcionalidades
- Extração da tabela de seções e do mapa de inundação do PAE de Jurumirim (prancha p. 38), georreferenciamento (RMS 0,47 m) e vetorização das manchas ZAS/ZSS.
- Sobreposição da envoltória com município e áreas urbanizadas (IBGE 2019), relevo (Copernicus GLO-30) e vias (OSM).
- Barragens a jusante (Piraju e Paranapanema): fatos dos PAEs, seções e tempos (Tabelas 9/10 lidas por OCR), ZAS como trecho de rio e estimativa exploratória de mancha para Piraju, rotulada e separada do dado oficial.
- Filtro de barragens («Por Barragem Isolada» ou «Todas barragens selecionadas») e métricas de exposição (pressão dinâmica, avanço lateral, altitude, % de área urbanizada).
- Dashboard Streamlit, 6 notebooks e imagens/vídeos de visão de drone.
- Rótulos persistentes: `DADO OFICIAL`, `DERIVADO DO PAE`, `ESTIMATIVA EXPLORATÓRIA`, `ILUSTRAÇÃO`.

## Resultados principais (derivados do PAE de Jurumirim, p. 38)
| Item | Resultado | Ressalva |
|---|---|---|
| Alcance modelado | ~33 km, até a barragem da UHE Piraju | o PAE não modela além dela |
| Envoltória de ruptura (ZAS+ZSS) | ≈ 30,4 km² (ZAS ≈ 6,8 km²) | vetorização por cor de raster; incerteza de metros a dezenas de metros |
| Fração do município de Piraju na envoltória | ≈ 5,3 % (26,8 de 506 km²) | predominantemente rural/ribeirinha |
| Maior mancha urbanizada (IBGE 2019) | ≈ 2,0 km da envoltória, sem interseção | IBGE 2019 não é perímetro urbano legal |
| Manchas urbanizadas pequenas que intersectam | 2 polígonos, 3.326 m² no total | mesma ordem da incerteza de digitalização |
| Tempo até a UHE Piraju | 1 h 59 min (sobrelevação >= 0,61 m) | tabelado no PAE |

A ruptura em cascata (Jurumirim, Piraju, Paranapanema) **não é modelada**: o modo «Todas barragens selecionadas» sobrepõe cenários isolados. Limitações completas: [guia técnico, seção 11](docs/GUIA_TECNICO.md#11-limitações-conhecidas).

![Corredor Jurumirim a Piraju em 3D](docs/img/3d_corredor.png)

## Arquitetura
```
PDFs oficiais (fora do Git) -> extração -> georreferência/vetorização --+
IBGE / Copernicus / OSM -> fetch_public_data.py -> SIG (interseções) ---+--> data/processed
                                                                         +--> app/ (Streamlit) · notebooks/ · docs/img
```

## Início rápido
Requer Python >= 3.11.
```bash
make setup     # cria .venv e instala dependências
make test      # suíte pytest
make run       # dashboard em http://localhost:8501
```
`make run` e `make test` funcionam sem os PDFs oficiais, com os dados processados versionados. Para refazer o pipeline (`make data`, `make dams`, `make estimates`, `make exposure`, `make notebooks`, `make drone`) consulte a [seção 3 do guia técnico](docs/GUIA_TECNICO.md#3-instalação-e-execução).

## Estrutura do repositório
```
app/            dashboard Streamlit
src/jurumirim/  pacote (extração, georreferência, vetorização, SIG, relevo, exposição, animação)
scripts/        pipelines e utilitários
notebooks/      01 extração · 02 CRS · 03 DEM · 04 interseção · 05 tempo e incerteza · 06 barragens a jusante
data/           raw (dados públicos), processed (derivados), metadata (procedência)
docs/           guia técnico, imagens e apresentação (PDF)
tests/          testes automatizados
```

## Dados e licenças
- Os PDFs dos PAEs e do PSB são documentos de terceiros e **não são redistribuídos** (ignorados pelo Git); o PSB de Piraju está marcado «Sigilo: Interno».
- IBGE (dados abertos), Copernicus DEM GLO-30 (licença Copernicus) e OpenStreetMap (ODbL 1.0), com atribuições no [guia técnico](docs/GUIA_TECNICO.md#13-licenças-e-atribuições).

## Documentação
- [Guia técnico](docs/GUIA_TECNICO.md): arquitetura, fontes, metodologia, validação, limitações, deploy e solução de problemas.
- [Apresentação (PDF)](docs/apresentacao/Jurumirim_Flood_Explorer.pdf).
- Cenário exploratório de volume (ANUGA), em repositório separado: [simulador-hidro-anuga](https://github.com/RenanCOliveira93/simulador-hidro-anuga); resumo na [seção 9 do guia](docs/GUIA_TECNICO.md#9-cenário-exploratório-de-volume-anuga).

## Licença
GPL-3.0. Ver [LICENSE](LICENSE).
