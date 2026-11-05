"""Extração da tabela de seções ST-xxx da prancha CTG-SB-DE-2415-JUR (PDF p. 38).

A tabela é texto vetorial no PDF; as palavras são agrupadas por linha (coordenada y)
e atribuídas a colunas pela ordem em x. Nenhum valor é inferido.
"""
from __future__ import annotations

import re

import pandas as pd
import pymupdf

from .paths import PDF

PAGE = 38  # página física do PDF (1-based)
COLUMNS = [
    "distancia_km", "x_utm", "y_utm", "sobrelevacao_m",
    "velocidade_ms", "tempo_chegada", "vazao_pico_m3s",
]
_NUM = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^\d+(,\d+)?$|^\d{2}:\d{2}$|^-$")


def parse_br_number(tok: str) -> float | None:
    """'7.432.016' -> 7432016.0 ; '29,72' -> 29.72 ; '-' -> None."""
    if tok.strip() == "-":
        return None
    return float(tok.replace(".", "").replace(",", "."))


def hhmm_to_minutes(tok: str) -> int:
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", tok.strip())
    if not m:
        raise ValueError(f"hh:mm inválido: {tok!r}")
    h, mi = int(m[1]), int(m[2])
    if mi >= 60:
        raise ValueError(f"minutos inválidos: {tok!r}")
    return h * 60 + mi


def extract_sections(pdf_path=PDF) -> pd.DataFrame:
    doc = pymupdf.open(pdf_path)
    page = doc[PAGE - 1]
    words = page.get_text("words")
    # âncoras: tokens ST-001..ST-017 dentro do quadro (x < 1100 pt), um por linha
    anchors = {}
    for w in words:
        if re.fullmatch(r"ST-\d{3}", w[4]) and w[0] < 1100 and w[1] < 700 and w[0] > 840:
            anchors.setdefault(w[4], (w[1] + w[3]) / 2)
    if not anchors:
        raise RuntimeError("Quadro de seções não encontrado na página 38")
    ids = sorted(anchors)
    ys = [anchors[i] for i in ids]
    rows = {i: [] for i in ids}
    # descrição = palavras entre ID e coluna de distância
    desc = {i: [] for i in ids}
    for w in words:
        if not (840 < w[0] < 1760 and 250 < w[1] < 700):
            continue
        yc = (w[1] + w[3]) / 2
        j = min(range(len(ys)), key=lambda k: abs(ys[k] - yc))
        if abs(ys[j] - yc) > 14:
            continue
        sid = ids[j]
        if w[0] >= 1180 and _NUM.match(w[4]):
            rows[sid].append((w[0], w[4]))
        elif 1065 < w[0] < 1180 and not re.fullmatch(r"ST-\d{3}", w[4]):
            desc[sid].append((round(yc / 8), w[0], w[4]))
    out = []
    for sid in ids:
        toks = [t for _, t in sorted(rows[sid])]
        if len(toks) != len(COLUMNS):
            raise RuntimeError(f"{sid}: esperado {len(COLUMNS)} valores, obtido {toks}")
        rec = {"id": sid}
        text = " ".join(t for _, _, t in sorted(desc[sid]))
        rec["descricao"] = text.strip()
        rec.update({
            "distancia_km": parse_br_number(toks[0]),
            "x_utm": parse_br_number(toks[1]),
            "y_utm": parse_br_number(toks[2]),
            "sobrelevacao_m": parse_br_number(toks[3]),
            "velocidade_ms": parse_br_number(toks[4]),
            "tempo_chegada_hhmm": toks[5],
            "tempo_chegada_min": hhmm_to_minutes(toks[5]),
            "vazao_pico_m3s": parse_br_number(toks[6]),
        })
        out.append(rec)
    df = pd.DataFrame(out)
    df["crs"] = "EPSG:31982"  # SIRGAS 2000 / UTM 22S
    df["pagina_fonte_pdf"] = PAGE
    df["fonte"] = "PAE UHE Jurumirim, prancha CTG-SB-DE-2415-JUR (quadro de seções)"
    return df
