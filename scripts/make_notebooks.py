#!/usr/bin/env python
"""Gera os notebooks didáticos em notebooks/ (execute com `make notebooks`)."""
from pathlib import Path

import nbformat as nbf

NB = Path(__file__).resolve().parents[1] / "notebooks"
NB.mkdir(exist_ok=True)
SETUP = ("import sys, warnings; warnings.filterwarnings('ignore')\n"
         "sys.path.insert(0, '../src')\n"
         "import pandas as pd, numpy as np, matplotlib.pyplot as plt\n"
         "pd.set_option('display.width', 200); pd.set_option('display.max_columns', 30)\n"
         "from jurumirim import DISCLAIMER\nprint(DISCLAIMER)")


def make(name, cells):
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.cells = [nbf.v4.new_markdown_cell(c) if k == "md" else nbf.v4.new_code_cell(c) for k, c in cells]
    nbf.write(nb, NB / name)


make("01_pae_extraction.ipynb", [
    ("md", "# 01 — Extração da tabela de seções do PAE\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "**Fonte:** PAE UHE Jurumirim (CTG-SB-PAEE-2026-R0-JUR), prancha CTG-SB-DE-2415-JUR — **página física 38** do PDF "
           "(não confundir com a numeração interna do PAE).\n\n"
           "Páginas auditadas: 21 (características), 37 (descrição do estudo), 38 (prancha), 52 (vale a jusante), 54-55 (tempo de chegada)."),
    ("code", SETUP),
    ("md", "## 1. Natureza da prancha\nA página 38 é uma prancha A1 (2384×1684 pt). A **tabela é texto vetorial**; o **mapa é raster** (41 faixas de imagem)."),
    ("code", "import pymupdf\nfrom jurumirim.paths import PDF\npage = pymupdf.open(PDF)[37]\nprint(page.rect, 'texto:', len(page.get_text()), 'chars | desenhos vetoriais:', len(page.get_drawings()), '| imagens:', len(page.get_images()))"),
    ("md", "## 2. Extração por coordenadas\nAs palavras do PDF são agrupadas por linha (coordenada *y* ao redor de cada ID `ST-xxx`) e ordenadas em *x*. "
           "Números BR (`7.432.016`, `29,72`) e `hh:mm` são convertidos; `-` vira `NaN` (nunca adivinhamos valores)."),
    ("code", "from jurumirim.pae import extract_sections, parse_br_number, hhmm_to_minutes\nsec = extract_sections()\nsec.drop(columns=['crs','fonte']).round(2)"),
    ("md", "## 3. Dupla checagem com a imagem\nA prancha foi renderizada e conferida visualmente linha a linha com o texto extraído. Abaixo, o recorte da tabela renderizado do próprio PDF."),
    ("code", "import io\nfrom PIL import Image\npix = page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6), clip=pymupdf.Rect(1000,130,1760,720))\nImage.open(io.BytesIO(pix.tobytes('png')))"),
    ("code", "# Checagens automáticas de consistência\nassert sec.distancia_km.is_monotonic_increasing and sec.tempo_chegada_min.is_monotonic_increasing\nassert sec.sobrelevacao_m.is_monotonic_decreasing\nprint('monotonicidade OK; pendente:', sec[sec.vazao_pico_m3s.isna()].id.tolist(), '(vazão ST-017 = \"-\" na fonte)')"),
    ("md", "## 4. Observações\n- 'Propriedas MD' (ST-012) é erro ortográfico da fonte e foi mantido.\n- O tempo de chegada refere-se à sobrelevação de **0,61 m (~2 ft)** (nota 2 da prancha).\n- Resultado salvo em `data/processed/pae_sections.csv`; procedência em `data/metadata/pae_provenance.json`."),
])

make("02_crs_georreferenciamento.ipynb", [
    ("md", "# 02 — CRS e georreferenciamento da prancha\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "A prancha informa **SIRGAS 2000 / UTM 22S (EPSG:31982)**. A grade UTM do mapa é **vetorial** no PDF (12 linhas); os rótulos "
           "(667000…682000 E; 7431000…7446000 N) identificam cada linha → 36 pontos de controle exatos."),
    ("code", SETUP),
    ("code", "from jurumirim.georef import fit_transform, section_lines, independent_check\nfrom jurumirim.pae import extract_sections\nA, info = fit_transform()\nprint(A)\n{k: v for k, v in info.items() if k != 'control_points'}"),
    ("md", "## Erro de registro (RMS)\nO RMS dos resíduos é submétrico — esperado, pois a grade é desenhada em posições exatas. "
           "Isso mede **só o registro da grade**, não a precisão do contorno do PAE."),
    ("code", "chk = independent_check(A, extract_sections(), section_lines())\ns = pd.Series(chk).round(1); print(s.to_string())\nprint('\\nST-001 (brecha) não tem traço próprio: fora da checagem; demais seções: máx =', s.drop('ST-001').max(), 'm')"),
    ("md", "## Por que isso importa\nCom a checagem independente (ponto central tabelado × traço de seção desenhado), 16/17 seções coincidem em <1 m — confirma que a transformação e a leitura das coordenadas estão consistentes."),
    ("code", "from pyproj import CRS, Transformer\nprint(CRS.from_epsg(31982).name)\nt = Transformer.from_crs(31982, 4326, always_xy=True)\nprint('Portaria UHE Jurumirim (X 680.478; Y 7.432.283) ->', t.transform(680478, 7432283))"),
])

make("03_dem_perfis.ipynb", [
    ("md", "# 03 — DEM (Copernicus GLO-30) e perfis\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "DEM: Copernicus GLO-30, ~30 m, **MDS** (inclui vegetação/edificações), datum horizontal WGS84, **vertical EGM2008**. "
           "Precisão vertical nominal < 4 m (90%). **Perfis são descritivos: não se infere alcance de inundação por comparação de cotas.**"),
    ("code", SETUP),
    ("code", "from jurumirim import data\nfrom jurumirim.terrain import section_geometries, profile, DEM_PATH\nfrom jurumirim.georef import fit_transform\nimport rasterio\nwith rasterio.open(DEM_PATH) as s: print(s.crs, s.res, s.shape, s.nodata)\nA,_ = fit_transform(); sec = data.sections(); geoms = section_geometries(A, sec)"),
    ("code", "fig, axes = plt.subplots(4, 4, figsize=(14, 9), sharey=False, constrained_layout=True)\nfor ax, (sid, g) in zip(axes.ravel(), [(k,v) for k,v in geoms.items() if v is not None]):\n    p = profile(g); ax.plot(p.dist_m, p.z_m, color='saddlebrown'); ax.set_title(sid, fontsize=9)\n    ax.set_xlabel('m ao longo da seção', fontsize=7); ax.grid(alpha=.3)\nfig.suptitle('Perfis de terreno (MDS Copernicus GLO-30) ao longo dos traços das seções — DERIVADO; apenas descritivo'); plt.show()"),
    ("md", "## Sensibilidade à resolução do DEM\nAgregamos o DEM (fator 3, ~90 m) e comparamos as cotas amostradas nas seções."),
    ("code", "from rasterio.enums import Resampling\nfrom jurumirim.terrain import sample_dem\nimport numpy as np, rasterio\nfrom pyproj import Transformer\nt = Transformer.from_crs(31982, 4326, always_xy=True)\nlon, lat = t.transform(sec.x_utm.values, sec.y_utm.values)\nwith rasterio.open(DEM_PATH) as src:\n    z30 = np.array([v[0] for v in src.sample(zip(lon, lat))], float)\n    arr = src.read(1, out_shape=(src.height//3, src.width//3), resampling=Resampling.average)\n    tr = src.transform * src.transform.scale(3, 3)\n    z90 = np.array([arr[rasterio.transform.rowcol(tr, x, y)] for x, y in zip(lon, lat)], float)\nd = pd.DataFrame({'id': sec.id, 'z30': z30, 'z90': z90, 'dif': z90 - z30}); print(d.round(1).to_string()); print('|dif| médio:', d.dif.abs().mean().round(2), 'm; máx:', d.dif.abs().max().round(2), 'm')"),
    ("md", "A diferença de poucos metros entre resoluções é comparável à incerteza vertical do DEM — mais um motivo para **não** usar cotas do DEM para refinar a mancha."),
])

make("04_analise_intersecao.ipynb", [
    ("md", "# 04 — Interseção: mancha do PAE × Piraju\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "Todas as áreas/distâncias em **EPSG:31982 (UTM 22S)**. Diferenciamos: **município de Piraju** (IBGE), **mancha urbanizada** (IBGE 2019 — não é o perímetro urbano legal) e **regiões ribeirinhas** (restante do município dentro da envoltória)."),
    ("code", SETUP),
    ("code", "from jurumirim import data, gis\nenv = data.envelope(); mun = data.municipios(); urb = data.urbanizadas()\nprint(mun.crs.is_projected, 'envoltória km²:', round(env.area/1e6,2))\nmo = gis.municipality_overlap(env, mun); mo.round(2)"),
    ("code", "uo = gis.urban_overlap(env, urb, mun); uo.head(10).round(2)"),
    ("code", "pir_m = mun[mun.codarea == gis.PIRAJU_CODE].geometry.iloc[0]\nin_pir = env.intersection(pir_m)\nprint(f'Envoltória dentro de Piraju: {in_pir.area/1e6:.1f} km² ({100*in_pir.area/pir_m.area:.1f}% do município)')\nus = data.urban_summary()\nprint(f\"Maior polígono urbanizado de Piraju: {us['main_area_km2']:.2f} km²; distância à envoltória {us['main_distance_m']:.0f} m; intersecta: {us['main_intersects']}\")\nprint(f\"Polígonos urbanizados de Piraju que intersectam a envoltória: {us['n_intersecting']} (total {us['intersecting_area_km2']*1e6:.0f} m²)\")\npd.DataFrame(us['intersecting_polygons'])"),
    ("code", "rc = gis.road_crossings(env, data.roads()); rc"),
    ("md", "## Leitura\n- Na digitalização, o **maior polígono urbanizado IBGE 2019 de Piraju não intersecta a envoltória** (~2 km de distância); **2 polígonos pequenos e pouco densos intersectam marginalmente** (centenas a poucos milhares de m², ≤1,1% de sua área) — ordem de grandeza da incerteza de digitalização. O PAE rotula ST-014/ST-015 como 'Área urbana Pirajú ME'.\n- A parte da envoltória dentro de Piraju é rural/ribeirinha (represa da UHE Piraju e entorno, propriedades — PAE p. 52).\n- A rodovia **SP-261** cruza a envoltória próximo à barragem (OSM).\n- Isso **não** é classificação de segurança de endereços."),
    ("code", "from jurumirim import plots\nfrom IPython.display import display\ndisplay(plots.overview_map())"),
])

make("05_tempo_chegada_incerteza.ipynb", [
    ("md", "# 05 — Tempo de chegada e avaliação de incerteza\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "Tempos: PAE p. 38 (quadro) e p. 55 (Figura 12). Definição: instante em que a onda atinge sobrelevação de 0,61 m."),
    ("code", SETUP),
    ("code", "from jurumirim import data, plots\nsec = data.sections()\nsec['celeridade_media_ms'] = sec.distancia_km.diff()*1000/(sec.tempo_chegada_min.diff()*60)\nsec[['id','distancia_km','tempo_chegada_hhmm','celeridade_media_ms']].round(2)"),
    ("md", "A 'celeridade média' entre seções (distância ao longo do rio ÷ intervalo de tempo) é **derivada** dos valores do PAE, só para leitura; **não** é um resultado hidráulico novo."),
    ("code", "from IPython.display import display\ndisplay(plots.section_charts())"),
    ("md", "## Incerteza posicional da mancha\nDeslocamos a envoltória (buffer ±d) para ver se a conclusão espacial sobre a mancha urbanizada de Piraju mudaria."),
    ("code", "from jurumirim import data\nenv = data.envelope(); mun = data.municipios(); urb = data.urbanizadas()\nfrom jurumirim import gis\npir_m = mun[mun.codarea == gis.PIRAJU_CODE].geometry.iloc[0]\nids = data.urban_summary()\nu = urb[urb.representative_point().within(pir_m)].copy()\nmain = u.loc[u.area.idxmax()].geometry\nrest = u.drop(u.area.idxmax()).geometry.union_all()\nrows = []\nfor d in (0, 10, 25, 50, 100, 250, 500, 1000):\n    e = env.buffer(d)\n    rows.append({'buffer_m': d, 'area_envoltoria_km2': e.area/1e6, 'maior_poligono_urbano_inter_km2': e.intersection(main).area/1e6, 'demais_poligonos_inter_km2': e.intersection(rest).area/1e6})\npd.DataFrame(rows).round(3)"),
    ("md", "Incertezas somadas: registro da grade (~0,5 m), vetorização (1-3 px ≈ 3,5-10 m), simplificação (2,5 m), incerteza do próprio PAE (modelo de terreno e escala 1:30.000 → ~15-30 m de largura de traço). "
           "A distância de ~2 km até o maior polígono urbanizado é **~2 ordens de grandeza maior** que a incerteza posicional (a conclusão 'sem interseção' para ele é robusta até ~1 km de buffer), enquanto as sobreposições marginais dos polígonos periféricos pequenos **não são robustas** (crescem com o buffer). Tudo vale **apenas para o cenário do PAE**."),
    ("code", "print('Distância do maior polígono urbanizado à envoltória (m):', round(main.distance(env)))"),
])

make("06_barragens_a_jusante.ipynb", [
    ("md", "# 06 — Barragens a jusante: Piraju e Paranapanema\n> **Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.**\n\n"
           "Fontes: **PAE UHE Piraju** (CBA, 3308-HID-CBA-A-RT-G00-0001), **PAE UHE Paranapanema** (Enel) e **PSB de Piraju** (resumo). "
           "Este notebook mostra como as tabelas foram lidas, como foram checadas e **o que não existe** nas fontes. "
           "**Ruptura em cascata não foi modelada**: aqui só há cenários *isolados*."),
    ("code", SETUP),
    ("md", "## 1. Numeração de páginas\nO PAE Piraju tem capa + 86 páginas numeradas: **página do PDF = impressa + 1**. O complemento do projeto cita páginas impressas. Abaixo, o rótulo 'Páginas: N de 86' lido de cada página do PDF."),
    ("code", "import pymupdf\nfrom jurumirim import cascade, paths\nif paths.PIRAJU_PDF.exists():\n    with pymupdf.open(paths.PIRAJU_PDF) as d:\n        print([(i, cascade._printed_page(d[i-1].get_text())) for i in (3, 45, 62, 63, 64, 82)], '(pág. PDF, impressa)')\nelse:\n    print('PDF do PAE Piraju ausente: célula ignorada (os dados processados já estão no repositório).')"),
    ("md", "## 2. As Tabelas 9 e 10 são imagens\nNão há texto extraível; foram lidas por **OCR** (RapidOCR, em duas escalas) a partir das imagens embutidas. O OCR é dependência *opcional* (`make ocr`); o resultado bruto fica versionado em `data/processed/dams/PIR/ocr_raw/`."),
    ("code", "from jurumirim import piraju_tables as pt\nD = paths.PROCESSED / 'dams' / 'PIR' / 'ocr_raw'\nt10a = pt.parse_table10(pt.load(D/'tabela10_top_s1.json'), pt.load(D/'tabela10_bottom_s1.json'))\nt10b = pt.parse_table10(pt.load(D/'tabela10_top_s1.5.json'), pt.load(D/'tabela10_bottom_s1.5.json'))\nt9a = pt.parse_table9(pt.load(D/'tabela9_s2.json')); t9b = pt.parse_table9(pt.load(D/'tabela9_s3.json'))\nprint('linhas T10:', len(t10a), '| T9:', len(t9a))\nprint('discordâncias entre escalas — T10:', pt.crosscheck(t10a, t10b), '| T9:', pt.crosscheck(t9a, t9b))\nt10a[t10a.tr_anos == 10000].head(8)"),
    ("md", "O parser **falha com erro** se uma linha não tiver exatamente o número esperado de campos (nada é adivinhado). Duas exceções conhecidas e tratadas: o `-` de ST-22 (tempo da onda) e as velocidades `-` de ST-00 na Tabela 9."),
    ("md", "## 3. Checagens independentes do OCR\nAs duas escalas usam o mesmo motor, então concordância mostra estabilidade, não verdade. Por isso há checagens **físicas**:"),
    ("code", "r = t10a.copy(); r['gap'] = r.elev_max_m - r.elev_fundo_m - r.prof_max_m\nn = t9a.copy(); n['gap'] = n.elev_max_m - n.elev_fundo_m - n.prof_max_m\nprint('cota − fundo − profundidade (m): T10', r.gap.min().round(2), '…', r.gap.max().round(2), '| T9', n.gap.min().round(2), '…', n.gap.max().round(2))\nm = t10a[t10a.tr_anos==10000].merge(t9a[t9a.tr_anos==10000], on='secao', suffixes=('_rup','_nat'))\nprint('T9×T10 (imagens distintas) coincidem em fundo e distância:', bool((m.elev_fundo_m_rup==m.elev_fundo_m_nat).all() and (m.distancia_km_rup==m.distancia_km_nat).all()))\nprint('ruptura ≥ cheia natural (cota máx., TR 10.000):', bool((m.elev_max_m_rup >= m.elev_max_m_nat).all()))\nfor tr, g in t10a.groupby('tr_anos'):\n    g = g.sort_values('secao'); print(f'TR {tr}: distância e tempo de chegada crescentes:', g.distancia_km.is_monotonic_increasing, g.t_frente_min.dropna().is_monotonic_increasing)"),
    ("md", "Uma ressalva importante: **os dois motores/leituras podem errar do mesmo jeito** e não houve revisão de engenheiro. Se você for citar um número, confira na página impressa 62 (Tabela 10) do PAE."),
    ("md", "## 4. Posição das seções de Piraju (ILUSTRAÇÃO)\nO PDF não traz coordenadas das seções. A Figura 17 (raster) tem grade UTM e rótulos ST-xx. Usamos **a distância do PAE ao longo do rio** para posicionar cada seção sobre o eixo do Rio Paranapanema (OSM) e validamos contra documentos independentes:"),
    ("code", "from jurumirim import dams as DM\nv = DM.validation()\nfor k in ['fig17_rms_m','fig17_n_control_points','fig17_pixel_size_m','km_osm_piraju_to_paranapanema_dam','km_pae_piraju_zas','pos_9_68km_to_official_paranapanema_dam_m','piraju_official_vs_jurumirim_st017_m','label_offset_m_min','label_offset_m_max']:\n    print(f'{k:48s}', v[k])\nprint(v['nota'])"),
    ("code", "import matplotlib.pyplot as plt\nfrom jurumirim import selection as S\nsel = S.make(S.MODE_TODAS, ['JUR','PIR','PAR'])\ns = S.sections_for(sel); rx, ry = DM.river_xy(); dp = DM.dam_points().set_index('dam')\nfig, ax = plt.subplots(figsize=(9, 5)); ax.plot(rx, ry, color='#9ecae1')\nfor dam, g in s.groupby('dam'): ax.scatter(g.x_utm, g.y_utm, c=DM.COLORS[dam], s=25, label=DM.DAMS[dam].name)\nfor dam in dp.index: ax.scatter(dp.loc[dam,'x_utm'], dp.loc[dam,'y_utm'], marker='s', s=90, c=DM.COLORS[dam], ec='k')\nax.set_aspect('equal'); ax.legend(); ax.set_title('Seções: Jurumirim (UTM do PAE) e Piraju (km sobre eixo OSM, ILUSTRAÇÃO)'); plt.show()"),
    ("md", "Duas coisas **não existem** nos PDFs: a **mancha georreferenciada** de Piraju (Apêndice 9 só lista os arquivos) e os **mapas/tempos** da Paranapanema (Figuras 2–6 são capturas do HEC-RAS sem coordenadas). Nada foi desenhado por suposição."),
    ("md", "## 5. O filtro: 'Por Barragem Isolada' × 'Todas barragens selecionadas'\n'Todas' **sobrepõe cenários isolados**; cada um usa o **relógio da própria ruptura**. Provamos que Piraju não depende de Jurumirim estar selecionada:"),
    ("code", "t = 30\nalone = S.state_at(S.make(S.MODE_ISOLADA, ['PIR']), t).reset_index(drop=True)\nboth = S.state_at(S.make(S.MODE_TODAS, ['JUR','PIR']), t); both = both[both.dam=='PIR'].reset_index(drop=True)\nprint('Estado de Piraju em t=30 min idêntico com/sem Jurumirim:', alone.equals(both))\nS.summary_at(S.make(S.MODE_TODAS, ['JUR','PIR','PAR']), 60)"),
    ("md", "## 6. Inconsistências nas próprias fontes\nRegistradas como publicadas; não foram corrigidas nem usadas em cálculos."),
    ("code", "f = DM.facts(); f[f.flag.notna()][['dam','label','value','unit','page_printed','page_pdf','note']]"),
    ("md", "## Limites\n- Sem hidrograma completo, sem mancha de Piraju/Paranapanema, sem estudo de cascata.\n- Pico de vazão não é hidrograma; comparar picos de estudos diferentes **não** prova falha nem segurança.\n- O PSB de Piraju traz 'Sigilo: Interno': confirme a possibilidade de divulgação antes de publicar derivados."),
])
print("notebooks gerados")
