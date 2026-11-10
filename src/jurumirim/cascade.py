"""Análise de cascata Jurumirim → Piraju → Paranapanema.

Regras: nenhum número é inventado; cada métrica carrega documento, página e cenário;
o cenário D (ruptura em cascata) é sempre ``not_modelled``. As afirmações do
COMPLEMENTO_PAE_UHE_PIRAJU.md (nota de pesquisa local, não versionada) são tratadas como *alegações não verificadas* até que o PDF
da Piraju esteja em ``data/raw/PAE_UHE_PIRAJU.pdf`` e seja conferido manualmente.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import pymupdf

from . import paths

DOC_JUR = "PAE Externo UHE Jurumirim (CTG-SB-PAEE-2026-R0-JUR), jan/2026"
DOC_PIR = "PAE UHE Piraju (CBA), 3308-HID-CBA-A-RT-G00-0001, emissão 20/10/2025"
DOC_PSB = "PSB UHE Piraju – Sumário Executivo (CBA), PIR-PS-00-RT rev. 00"
DOC_PAR = "PAE UHE Paranapanema (Enel Green Power), GRE.OEM.R.88.BR.H.01111.09.003.08, rev. 08"
DOC_COMPL = "COMPLEMENTO_PAE_UHE_PIRAJU.md (nota de pesquisa do projeto)"
PIRAJU_URL = "https://d3ltu4sfk36jla.cloudfront.net/cba/PIRAJU_TARJADO_para_site_76f2c48308.pdf"

SCENARIO_STATUS = {"documented", "extracted_pending_review", "source_unavailable", "not_modelled"}

# Alegações do complemento. 'page_ref_as_given' usa a numeração IMPRESSA do PAE Piraju (confirmado: PDF = impressa + 1).
CLAIMS = [
    dict(id="C-01", scenario="D", numbers=["articulação", "ruptura isolada"], page_ref_as_given="58-59", pdf_pages_expected=[59],
         text="O PAE Piraju registra articulação dos empreendedores para estudo comum de rompimento em cascata, "
              "mas adota ruptura isolada de Piraju (seção 5.3.1).",
         manual=dict(pages_printed=[58], note="Seção 5.3.1 ocupa as p. 57-58 impressas; articulação e 'ruptura isolada' estão na p. 58.")),
    dict(id="C-02", scenario="B", numbers=["4.856", "2.829", "41,7", "532,66", "534,00", "1,34"], page_ref_as_given="44", pdf_pages_expected=[45],
         text="Cheia natural decamilenar 4.856 m³/s; amortecida por Jurumirim 2.829 m³/s (−41,7%); nível calculado "
              "532,66 m; crista 534,00 m; borda livre 1,34 m.",
         manual=dict(pages_printed=[44], note="Tabela 8 e texto da p. 44 impressa.")),
    dict(id="C-03", scenario="B", numbers=["pequeno volume"], page_ref_as_given="44", pdf_pages_expected=[45],
         text="O reservatório de Piraju tem capacidade limitada de amortecimento de grandes cheias.",
         manual=dict(pages_printed=[44], note="'não apresenta volume significativo para proporcionar o amortecimento de cheias'.")),
    dict(id="C-04", scenario="C", numbers=["35,9", "HEC-RAS"], page_ref_as_given="57", pdf_pages_expected=[58],
         text="Estudo de ruptura hipotética atualizado pela HIDROBR (2023), HEC-RAS 6.3.1, MDT de 35,9 km² a jusante.",
         manual=dict(pages_printed=[57], note="HBR036-23-CBA-PIR-REL-003_R02, mai/2023; MDT Topocart.")),
    dict(id="C-05", scenario="C", numbers=["531,50", "532,70"], page_ref_as_given="59-60", pdf_pages_expected=[61],
         text="Cenários TR 10 e 10.000 anos, sem ruptura e com ruptura isolada; cotas iniciais de ruptura 531,50 m e 532,70 m.",
         manual=dict(pages_printed=[59, 60], note="Cenários na p. 59; cotas iniciais, brecha e tempo de formação na p. 60.")),
    dict(id="C-06", scenario="C", numbers=["9,68", "Paranapanema"], page_ref_as_given="63", pdf_pages_expected=[64],
         text="Trecho a jusante estudado vai até a UHE Paranapanema, ≈ 9,68 km.",
         manual=dict(pages_printed=[63], note="Atenção: a ZAS (9,68 km) termina na Paranapanema, mas as Tabelas 9/10 vão até 32,35 km (ST-22).")),
    dict(id="C-07", scenario="C", numbers=["APÊNDICE 9"], page_ref_as_given="81", pdf_pages_expected=[82],
         text="Apêndices 8 e 9 identificam memoriais e mapas de inundação; disponibilidade dos anexos a conferir.",
         manual=dict(pages_printed=[81], note="Apêndices só LISTAM os documentos (HBR036-…, G5-945-…, 3308-HID-CBA-A-DE-G00-0001); não estão no PDF.")),
]

TOPICS = {
    "cota_crista": r"cota da crista|crista da barragem|El\.? ?crista",
    "niveis_operacionais": r"N\.?A\.? m[aá]ximo|n[ií]vel operacional|n[ií]veis operacionais",
    "vertedouro": r"vertedour|descarga",
    "hidrograma": r"hidrograma",
    "cheia_projeto": r"cheia de projeto|decamilenar|TR ?= ?10\.?000",
    "modelo_contorno": r"HEC-RAS|condi[cç][õo]es de contorno",
    "zas_zss": r"\bZAS\b|\bZSS\b",
    "mancha": r"mancha de inunda",
    "paranapanema": r"UHE Paranapanema",
    "cascata": r"cascata",
}

GAPS = [
    ("Mapas de inundação de Piraju (Apêndice 9: G5-945-PIR-DE-PAE-0001 e 3308-HID-CBA-A-DE-G00-0001)",
     "O PDF só LISTA os arquivos; sem mancha georreferenciada de Piraju.", "solicitar/obter com a CBA ou na página do PAE"),
    ("Memorial do estudo de ruptura de Piraju (HBR036-23-CBA-PIR-REL-003_R02, HIDROBR 2023)",
     "Apêndice 8 só lista o arquivo; hidrogramas e condições de contorno ficam no memorial.", "solicitar à CBA"),
    ("Mapas de inundação da Paranapanema (Anexos 1-2, cenários C1-C5)",
     "O PDF só lista os arquivos; Figuras 2-6 são capturas do HEC-RAS sem coordenadas. Tempos e velocidades estão nesses mapas.",
     "solicitar à Enel Green Power"),
    ("Hidrograma completo da ruptura de Jurumirim até Piraju",
     "O PAE Jurumirim dá só vazão de pico; ST-017 não tem vazão ('-').", "solicitar à CTG"),
    ("Estudo conjunto de ruptura em cascata (Jurumirim, Piraju, Paranapanema e demais)",
     "Piraju registra que os empreendedores 'estão em articulação'; sem resultado público conhecido.", "solicitar à CBA, CTG e Enel"),
    ("Análise estrutural/hidráulica de Piraju e Paranapanema sob onda vinda de montante",
     "Inexistente nas fontes; os PAEs de cada barragem adotam ruptura ISOLADA.", "estudo especializado"),
    ("Tabela de seções com tempos de chegada da Paranapanema", "Não consta do PDF.", "extrair dos mapas do Anexo 2 (se obtidos)"),
    ("Arquivos GIS (Jurumirim, Piraju, Paranapanema)", "Só há mapas em PDF/raster.", "solicitar aos empreendedores"),
]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_info(path: Path) -> dict:
    if not path.exists():
        return {"status": "source_unavailable", "sha256": None, "n_pages": None, "file_size_bytes": None}
    with pymupdf.open(path) as d:
        n = len(d)
    return {"status": "available", "sha256": sha256(path), "n_pages": n, "file_size_bytes": path.stat().st_size}


def source_registry(piraju_pdf: Path | None = None) -> list[dict]:
    piraju_pdf = piraju_pdf or paths.PIRAJU_PDF

    def rel(p: Path) -> str:
        return str(p.relative_to(paths.ROOT)) if p.is_relative_to(paths.ROOT) else str(p)

    return [
        dict(id="SRC-JUR", title="PAE Externo UHE Jurumirim", issuer="CTG Brasil", code="CTG-SB-PAEE-2026-R0-JUR",
             edition="R0, jan/2026; prancha CTG-SB-DE-2415-JUR", url="https://www.ctgbr.com.br/sustentabilidade/social/seguranca-da-comunidade/pae/pae-arquivos/", local_path=rel(paths.PDF),
             author_note="Arquivo renomeado pelo usuário (antes CTG-SB-PAEE-2026-R0-JUR.pdf); mesmo conteúdo.", **_pdf_info(paths.PDF)),
        dict(id="SRC-PIR", title="PAE UHE Piraju", issuer="CBA / Votorantim; estudo HIDROBR (2023); espacialização HEAD5 (2025)",
             code="3308-HID-CBA-A-RT-G00-0001", edition="emissão 20/10/2025; capa: REV5 nov/2025 (CV2117-PIR-PA-00-RT-0001)",
             url=PIRAJU_URL, local_path=rel(piraju_pdf),
             author_note="Versão 'tarjada para site'. 86 páginas numeradas + capa (PDF = impressa + 1). "
                         "Apêndices 8 e 9 apenas listados.", **_pdf_info(piraju_pdf)),
        dict(id="SRC-PSB", title="PSB UHE Piraju – Sumário Executivo", issuer="CBA", code="PIR-PS-00-RT", edition="rev. 00",
             url="https://d3ltu4sfk36jla.cloudfront.net/cba/PSB_Sumario_Executivo_UHE_Piraju_fd580524df.pdf", local_path=rel(paths.PSB_PIRAJU_PDF),
             author_note="Cabeçalho do documento: 'Sigilo: Interno'. Confirmar que pode ser divulgado antes de publicar derivados; "
                         "dados derivados ficam fora do Git (psb_*).", **_pdf_info(paths.PSB_PIRAJU_PDF)),
        dict(id="SRC-PAR", title="PAE UHE Paranapanema", issuer="Enel Green Power (EGP Paranapanema S/A)",
             code="GRE.OEM.R.88.BR.H.01111.09.003.08", edition="rev. 08, 15/12/2025 (corpo a partir da p.14 cita .05)",
             url="https://www.enel.com.br/pt-saopaulo/quemsomos/archive/d2018-comportamento-etico/plano-de-acao-de-emergencia.html",
             local_path=rel(paths.PARANAPANEMA_PDF),
             author_note="21 páginas ('PAGE n of 21' = página do PDF). Mapas (Anexos 1-2) não incluídos; contém contatos pessoais "
                         "(não reproduzidos).", **_pdf_info(paths.PARANAPANEMA_PDF)),
        dict(id="SRC-COMPL", title="Complemento técnico PAE Piraju", issuer="projeto (nota de pesquisa)", code=None,
             edition="sem data", url=None, local_path="COMPLEMENTO_PAE_UHE_PIRAJU.md",
             author_note="Fonte secundária; alegações conferidas contra o PDF da Piraju (ver claims).",
             status="secondary_checked" if piraju_pdf.exists() else "secondary_unverified",
             sha256=sha256(paths.ROOT / "COMPLEMENTO_PAE_UHE_PIRAJU.md"), n_pages=None, file_size_bytes=None),
    ]


def piraju_available(piraju_pdf: Path | None = None) -> bool:
    return (piraju_pdf or paths.PIRAJU_PDF).exists()


# ---------------------------------------------------------------- extração do PDF da Piraju
def _printed_page(text: str) -> int | None:
    """'Páginas: 44 de 86' (PAE Piraju) ou 'PAGE 15 of 21' (PAE Paranapanema); None se não houver rótulo."""
    m = re.search(r"P[áa]ginas?:?\s*(\d+)\s+de\s+\d+", text, re.I) or re.search(r"PAGE\s*(\d+)\s+of\s+\d+", text)
    return int(m.group(1)) if m else None


def extract_piraju(piraju_pdf: Path | None = None, out_dir: Path | None = None, save_figures: bool = True) -> dict:
    """Extrai texto, evidências por tema, tabelas e figuras. Sem PDF: grava só o status.

    Todo registro sai com verified=False: a conferência manual das tabelas críticas é obrigatória.
    """
    piraju_pdf = piraju_pdf or paths.PIRAJU_PDF
    out_dir = out_dir or paths.PROCESSED
    out_dir.mkdir(parents=True, exist_ok=True)
    doc_name = DOC_PIR
    if not piraju_pdf.exists():
        status = dict(status="source_unavailable", document=doc_name, expected_path=str(piraju_pdf),
                      generated_on=str(date.today()),
                      how_to_obtain=["Baixar a versão pública da CBA/Votorantim (URL em docs/GUIA_TECNICO.md) "
                                     "ou solicitá-la à CBA.", f"Salvar como {piraju_pdf}", "Rodar `make piraju`."])
        (out_dir / "piraju_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2))
        return status

    pages, evidence, tables, figures = [], [], [], []
    fig_dir = out_dir / "piraju_figures"
    with pymupdf.open(piraju_pdf) as d:
        for i, page in enumerate(d, 1):
            text = page.get_text()
            printed = _printed_page(text)
            pages.append(dict(source_page=i, printed_page=printed, n_chars=len(text), text=text))
            flat = " ".join(text.split())
            for topic, rx in TOPICS.items():
                for m in re.finditer(rx, flat, re.I):
                    a, b = max(0, m.start() - 120), min(len(flat), m.end() + 180)
                    evidence.append(dict(topic=topic, source_page=i, printed_page=printed, snippet=flat[a:b],
                                         source_document=doc_name, extraction_method="pymupdf_text_regex", verified=False))
                    break  # um trecho por tema e página
            try:
                for t_i, t in enumerate(page.find_tables().tables):
                    rows = t.extract()
                    if rows and len(rows) > 1:
                        tables.append(dict(table_id=f"p{i}-t{t_i}", source_page=i, printed_page=printed, rows=rows,
                                           source_document=doc_name, extraction_method="pymupdf_find_tables", verified=False))
            except Exception:  # noqa: BLE001 - tabelas sem estrutura detectável não são erro
                pass
            if save_figures:
                for img in page.get_images(full=True):
                    xref = img[0]
                    pix = pymupdf.Pixmap(d, xref)
                    if pix.width < 300 or pix.height < 300:
                        continue
                    if pix.colorspace and pix.colorspace.n > 3:
                        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                    fig_dir.mkdir(exist_ok=True)
                    fp = fig_dir / f"p{i:03d}_x{xref}.png"
                    pix.save(fp)
                    figures.append(dict(source_page=i, printed_page=printed, file=fp.name, width=pix.width,
                                        height=pix.height, source_document=doc_name,
                                        extraction_method="pymupdf_embedded_image", verified=False))
    pd.DataFrame(pages).to_csv(out_dir / "piraju_pages.csv", index=False)
    (out_dir / "piraju_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=1))
    (out_dir / "piraju_tables.json").write_text(json.dumps(tables, ensure_ascii=False, indent=1))
    (out_dir / "piraju_figures.json").write_text(json.dumps(figures, ensure_ascii=False, indent=1))
    claims = verify_claims(piraju_pdf)
    (out_dir / "piraju_claims_check.json").write_text(json.dumps(claims, ensure_ascii=False, indent=1))
    status = dict(status="extracted_pending_review", document=doc_name, sha256=sha256(piraju_pdf), n_pages=len(pages),
                  n_evidence=len(evidence), n_tables=len(tables), n_figures=len(figures), generated_on=str(date.today()),
                  note="Todos os registros verified=false até conferência manual das tabelas críticas.")
    (out_dir / "piraju_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2))
    return status


def verify_claims(piraju_pdf: Path | None = None) -> list[dict]:
    """Estado de cada alegação do complemento.

    `verified` = existe registro de conferência manual (leitura da página do PDF; assistente, não engenheiro).
    Com o PDF presente, também procura o texto/números nas páginas esperadas (`text_match`, `page_confirmed`).
    """
    piraju_pdf = piraju_pdf or paths.PIRAJU_PDF
    texts = None
    if piraju_pdf.exists():
        with pymupdf.open(piraju_pdf) as d:
            texts = [" ".join(p.get_text().split()) for p in d]
    out = []
    for c in CLAIMS:
        base = {k: v for k, v in c.items() if k != "manual"}
        manual = c.get("manual")
        base.update(verified=bool(manual), status="verified_manual" if manual else "reported_unverified",
                    verified_by=VERIFIED_BY if manual else None, verified_pages_printed=(manual or {}).get("pages_printed", []),
                    verification_note=(manual or {}).get("note", ""))
        if texts is None:
            base.update(text_match=None, found_on_pages=[], page_confirmed=None)
        else:
            found = [i for i, t in enumerate(texts, 1) if all(n in t for n in c["numbers"])]
            base.update(text_match=bool(found), found_on_pages=found,
                        page_confirmed=bool(set(found) & set(c["pdf_pages_expected"])))
            if not found:
                base["status"] = "no_text_match"
        out.append(base)
    return out


VERIFIED_BY = "leitura da página do PDF em 2026-11-05 (assistente; sem revisão de engenheiro)"


def load_extraction(name: str, base: Path | None = None):
    f = (base or paths.PROCESSED) / name
    return json.loads(f.read_text()) if f.exists() else None


# ---------------------------------------------------------------- métricas e cenários
def _sections() -> pd.DataFrame:
    return pd.read_csv(paths.PROCESSED / "pae_sections.csv")


def _pir_rupture() -> pd.DataFrame | None:
    f = paths.PROCESSED / "dams" / "PIR" / "sections_rupture.csv"
    return pd.read_csv(f) if f.exists() else None


def metrics(piraju_pdf: Path | None = None) -> pd.DataFrame:
    """Métricas exibíveis; cada linha tem documento, página e cenário."""
    sec = _sections().set_index("id")
    rows = []

    def add(scenario, name, value, unit, doc, page, note=""):
        rows.append(dict(scenario=scenario, metric=name, value=value, unit=unit, source_document=doc,
                         source_page=page, status="documented", note=note))

    b, last, near = sec.loc["ST-001"], sec.loc["ST-017"], sec.loc["ST-016"]
    add("A", "Vazão de pico na brecha (ST-001)", b.vazao_pico_m3s, "m³/s", DOC_JUR, "38 (PDF)")
    add("A", "Sobrelevação na brecha (ST-001)", b.sobrelevacao_m, "m", DOC_JUR, "38 (PDF)")
    add("A", "Vazão de pico próximo à UHE Piraju (ST-016)", near.vazao_pico_m3s, "m³/s", DOC_JUR, "38 (PDF)",
        "Pico apenas; não é hidrograma.")
    add("A", "Distância brecha → UHE Piraju (ST-017)", last.distancia_km, "km", DOC_JUR, "38 (PDF)")
    add("A", "Tempo de chegada da onda à UHE Piraju (ST-017)", int(last.tempo_chegada_min), "min", DOC_JUR, "38 e 55 (PDF)")
    add("A", "Vazão de pico em ST-017", None, "m³/s", DOC_JUR, "38 (PDF)", "PAE registra '-' (sem valor); não estimado.")
    r = _pir_rupture()
    if r is not None:
        r = r[r.tr_anos == 10000].set_index("secao")
        pg = "62 impressa / 63 PDF (Tabela 10)"
        add("C", "Vazão de pico no eixo da barragem de Piraju (ST-01), TR 10.000", r.loc["ST-01", "vazao_max_m3s"], "m³/s", DOC_PIR, pg)
        add("C", "Tempo da onda até ST-11 (km 9,65), TR 10.000", r.loc["ST-11", "t_frente_min"], "min", DOC_PIR, pg,
            "UHE Paranapanema está a 9,68 km (PAE Piraju, p.63 impressa).")
        add("C", "Tempo da onda até ST-12 (km 9,86), TR 10.000", r.loc["ST-12", "t_frente_min"], "min", DOC_PIR, pg)
        add("C", "Tempo da onda até ST-21 (km 29,50), TR 10.000", r.loc["ST-21", "t_frente_min"], "min", DOC_PIR, pg)
        add("C", "Vazão máxima em ST-22 (km 32,35), TR 10.000 [asterisco sem nota na página]", r.loc["ST-22", "vazao_max_m3s"],
            "m³/s", DOC_PIR, pg, "Ponto final no reservatório de Chavantes (N.A. de fundo 474 m na Tabela 9).")
    return pd.DataFrame(rows)


def scenarios(piraju_pdf: Path | None = None, out_dir: Path | None = None) -> list[dict]:
    have_c = _pir_rupture() is not None
    return [
        dict(id="A", name="Ruptura isolada de Jurumirim (dia seco, N.A. 568,00 m)", status="documented",
             source_document=DOC_JUR, source_page="21, 37, 38, 52, 54, 55 (PDF)",
             note="Mapa e tabela oficiais; modelagem termina na barragem de Piraju (~33 km)."),
        dict(id="B", name="Cheia de projeto (TR 10.000 anos) sem ruptura (Jurumirim)", status="documented",
             source_document=DOC_JUR, source_page="38 (PDF)",
             note="Só contorno no mapa; digitalização de baixa confiança; sem tabela hidráulica."),
        dict(id="C", name="Ruptura isolada de Piraju (TR 10.000 e TR 10 anos)",
             status="documented" if have_c else "source_unavailable",
             source_document=DOC_PIR, source_page="57-63 impressas (Tabelas 9 e 10: 62-63 PDF)" if have_c else "indisponível",
             note="Tabelas de 23 seções transcritas por OCR com checagens (ver Método). Mancha georreferenciada: INDISPONÍVEL "
                  "(mapas no Apêndice 9 não constam do PDF)." if have_c else "Sem o PDF não há dado verificado."),
        dict(id="C2", name="Ruptura isolada da Paranapanema (PAE Paranapanema)", status="documented",
             source_document=DOC_PAR, source_page="14-18",
             note="Só resumo: cenários de vazão/N.A., mancha ≈ 3,4 km², ZAS 10 km. Sem tabela de seções, sem tempos "
                  "(estão nos mapas do Anexo 2, não incluídos)."),
        dict(id="D", name="Ruptura em cascata Jurumirim → Piraju → Paranapanema", status="not_modelled",
             source_document="—", source_page="—",
             note="Nenhum estudo ou simulação hidráulica validada. Nenhuma mancha, tempo ou probabilidade é produzida."),
    ]


# ---------------------------------------------------------------- validações
def validate(piraju_pdf: Path | None = None, out_dir: Path | None = None) -> list[dict]:
    """Lista de checagens {check, ok, detail}. Falha = ok False."""
    res = []

    def chk(name, ok, detail=""):
        res.append(dict(check=name, ok=bool(ok), detail=detail))

    sec = _sections()
    req = ["id", "descricao", "distancia_km", "x_utm", "y_utm", "tempo_chegada_min", "pagina_fonte_pdf", "crs"]
    chk("campos obrigatórios das seções", all(c in sec.columns for c in req))
    ids = list(sec.id)
    chk("seções ST-001..ST-017 em ordem", ids == [f"ST-{i:03d}" for i in range(1, 18)], str(ids[:3]))
    chk("distâncias estritamente crescentes", sec.distancia_km.is_monotonic_increasing and sec.distancia_km.is_unique)
    chk("tempos de chegada não decrescentes", sec.tempo_chegada_min.is_monotonic_increasing)
    num = sec[["distancia_km", "sobrelevacao_m", "velocidade_ms", "tempo_chegada_min", "vazao_pico_m3s"]]
    chk("valores não negativos", (num.dropna() >= 0).all().all())
    chk("CRS único EPSG:31982 (SIRGAS 2000 / UTM 22S)", set(sec.crs) == {"EPSG:31982"})
    chk("origem (página) em todas as seções", sec.pagina_fonte_pdf.notna().all())

    m = metrics(piraju_pdf)
    chk("toda métrica tem documento, página e cenário",
        m[["source_document", "source_page", "scenario"]].notna().all().all() and (m.source_page != "").all())
    chk("unidades presentes e conhecidas", set(m.unit) <= {"m³/s", "m", "km", "min", "km²"})

    sc = {s["id"]: s for s in scenarios(piraju_pdf, out_dir)}
    chk("cenários A–D presentes", {"A", "B", "C", "D"} <= set(sc))
    chk("status de cenário válidos", all(s["status"] in SCENARIO_STATUS for s in sc.values()))
    chk("cenário D permanece not_modelled", sc["D"]["status"] == "not_modelled")
    chk("cenário C sem dado nem PDF é source_unavailable",
        _pir_rupture() is not None or sc["C"]["status"] == "source_unavailable")

    cl = verify_claims(piraju_pdf)
    chk("alegação 'verified' só com registro de conferência manual",
        all((not c["verified"]) or (c["verified_by"] and c["verified_pages_printed"]) for c in cl))
    chk("alegações têm cenário e página citada", all(c["scenario"] in sc and c["page_ref_as_given"] for c in cl))
    if piraju_pdf is None or piraju_pdf.exists():
        chk("alegações com números casam com o texto do PDF Piraju",
            all(c["text_match"] in (True, None) and c["page_confirmed"] in (True, None) for c in cl),
            str([c["id"] for c in cl if c["text_match"] is False or c["page_confirmed"] is False]))

    # --- dados das barragens a jusante
    d = paths.PROCESSED / "dams"
    if (d / "PIR" / "sections_rupture.csv").exists():
        r = pd.read_csv(d / "PIR" / "sections_rupture.csv")
        n = pd.read_csv(d / "PIR" / "sections_natural.csv")
        chk("Piraju: 23 seções × 2 TR (Tabela 10) e × 5 TR (Tabela 9)", len(r) == 46 and len(n) == 115, f"{len(r)}/{len(n)}")
        chk("Piraju: valores não negativos", (r.select_dtypes("number").dropna() >= 0).all().all())
        ok = all(g.sort_values("secao").distancia_km.is_monotonic_increasing and
                 g.sort_values("secao").t_frente_min.dropna().is_monotonic_increasing for _, g in r.groupby("tr_anos"))
        chk("Piraju: distâncias e tempos de chegada crescentes por TR", ok)
        gap = (r.elev_max_m - r.elev_fundo_m - r.prof_max_m)
        chk("Piraju: cota − fundo − profundidade em [0; 2] m (detecta erro de dígito do OCR)",
            gap.between(-0.05, 2.0).all(), f"min {gap.min():.2f} max {gap.max():.2f}")
        a = r[r.tr_anos == 10000].set_index("secao"); b = n[n.tr_anos == 10000].set_index("secao")
        chk("Piraju: Tabelas 9 e 10 (imagens distintas) coincidem em fundo e distância",
            (a.elev_fundo_m == b.elev_fundo_m).all() and (a.distancia_km == b.distancia_km).all())
        chk("Piraju: ruptura ≥ cheia natural na mesma TR (cota máxima)", (a.elev_max_m >= b.elev_max_m - 1e-9).all())
        v = json.loads((d / "validation.json").read_text())
        chk("OCR em duas escalas sem discordâncias (T9 e T10)",
            not v["tabela10_discordancias_ocr"] and not v["tabela9_discordancias_ocr"])
        chk("Fig.17: RMS das cruzes de controle ≤ 15 m", v["fig17_rms_m"] <= 15, f"{v['fig17_rms_m']} m")
        chk("Posição por km: 9,68 km do eixo cai a ≤ 100 m da coordenada oficial da Paranapanema",
            v["pos_9_68km_to_official_paranapanema_dam_m"] <= 100, f"{v['pos_9_68km_to_official_paranapanema_dam_m']} m")
        chk("Coordenada oficial de Piraju ≈ ST-017 do PAE Jurumirim (≤ 100 m)",
            v["piraju_official_vs_jurumirim_st017_m"] <= 100, f"{v['piraju_official_vs_jurumirim_st017_m']} m")
        chk("Quilometragem OSM Piraju→Paranapanema ≈ 9,68 km do PAE (≤ 0,15 km)",
            abs(v["km_osm_piraju_to_paranapanema_dam"] - v["km_pae_piraju_zas"]) <= 0.15,
            f"{v['km_osm_piraju_to_paranapanema_dam']} km")
    fs = [pd.read_csv(f) for f in sorted(d.glob("*/facts.csv"))]
    if fs:
        f = pd.concat(fs)
        chk("todo fato tem documento e página", f.source_document.notna().all() and f.page_pdf.notna().all(), f"{len(f)} fatos")
        chk("nenhum contato pessoal nos fatos", not f.astype(str).apply(lambda c: c.str.contains(r"\(\d{2}\) ?\d{4,5}-?\d{4}")).any().any())
    return res


def write_registry(out: Path | None = None) -> Path:
    out = out or paths.METADATA / "source_registry.json"
    out.write_text(json.dumps(dict(generated_on=str(date.today()), sources=source_registry(),
                                   claims=verify_claims(), gaps=[dict(item=a, status=b, next=c) for a, b, c in GAPS]),
                              ensure_ascii=False, indent=2))
    return out
