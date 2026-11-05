# Dados

| Dado | Fonte | Licença | Datum / resolução | Arquivo |
|---|---|---|---|---|
| Seções ST, mancha | PAE UHE Jurumirim (PDF do usuário) | documento de terceiros — **não** redistribuído neste repositório se o PDF for omitido | UTM 22S SIRGAS 2000 | `data/processed/pae_*` |
| Município | IBGE malha municipal v3 (API) | dados abertos IBGE | SIRGAS 2000; malha intermediária (~1:250.000) | `data/raw/ibge_municipios_sp.geojson` |
| Áreas urbanizadas | IBGE Áreas Urbanizadas do Brasil 2019 | dados abertos IBGE | SIRGAS 2000; ~1:100.000 | `data/raw/ibge_areas_urbanizadas_2019_regiao.gpkg` |
| Relevo | Copernicus DEM GLO-30 (AWS Open Data) | licença Copernicus (atribuição) | WGS84 / vertical EGM2008, ~30 m, MDS, erro < 4 m (90 %) | `data/raw/copernicus_glo30_jurumirim_piraju.tif` |
| Vias | OpenStreetMap (Overpass) | ODbL 1.0 | WGS84 | `data/raw/osm_roads.json` |

| Seções de Piraju (Tabelas 9/10) | PAE UHE Piraju, p. 61–62 impressas (imagens → OCR) | documento de terceiros, fora do Git | distância em km (posição ILUSTRATIVA) | `data/processed/dams/PIR/` |
| Fatos de Piraju/Paranapanema | PAE Piraju, PAE Paranapanema, PSB | terceiros; **PSB «Sigilo: Interno»** (derivados fora do Git) | — | `data/processed/dams/*/facts.csv` |
| Eixo do rio | OpenStreetMap (waterway) | ODbL 1.0 | WGS84 | `data/raw/osm_waterways.json` |

Datas de download, URLs e observações: `data/metadata/public_data_sources.json` (gerado por `scripts/fetch_public_data.py`).
Procedência do PAE, RMS e qualidade da vetorização: `data/metadata/pae_provenance.json`.
OSM `landuse` urbano de Piraju é praticamente vazio (7 elementos) e **não** foi usado como proxy de área urbana.
