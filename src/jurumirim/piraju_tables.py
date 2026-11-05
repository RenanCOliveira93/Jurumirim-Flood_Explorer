"""Parser das Tabelas 9 e 10 do PAE UHE Piraju (imagens embutidas, lidas por OCR).

Entrada: JSON bruto de scripts/ocr_pae_images.py. Cada linha deve ter exatamente o número de campos
esperado; qualquer divergência levanta ValueError (nada é adivinhado). A mesma tabela é lida em duas
escalas e `crosscheck` lista toda célula em que as leituras discordam.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROW_ID = re.compile(r"^ST[-–—]?\s?(\d{2})$")
T10_COLS = ["distancia_km", "elev_fundo_m", "prof_max_m", "vel_max_ms", "elev_max_m", "vazao_max_m3s",
            "t_pico_min", "t_frente_min"]
T9_TR = ["2", "5", "10", "50", "10000"]


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def rows_of(items: list[dict], tol: float) -> list[list[dict]]:
    out: list[list[dict]] = []
    for it in sorted(items, key=lambda i: (i["y0"] + i["y1"]) / 2):
        y = (it["y0"] + it["y1"]) / 2
        if out and abs(out[-1][0] - y) < tol:
            out[-1][1].append(it)
        else:
            out.append([y, [it]])
    return [sorted(r[1], key=lambda i: i["x0"]) for r in out]


def num(tok: str, flow: bool = False) -> float | None:
    """'7,44'->7.44 ; '26.857'->26857 (vazão) ; '7.00' (ruído de OCR)->7.0 ; '-'->None ; '2.834*'->2834."""
    t = tok.strip().replace(" ", "").replace("*", "").replace("—", "-").replace("–", "-")
    if t in {"-", ""}:
        return None
    if flow:
        if not re.fullmatch(r"\d{1,2}\.\d{3}", t):
            raise ValueError(f"vazão fora do formato: {tok!r}")
        return float(t.replace(".", ""))
    t = t.replace(",", ".")
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        raise ValueError(f"número fora do formato: {tok!r}")
    return float(t)


def _split(row: list[dict]):
    """Divide a linha em blocos que começam em cada 'ST-xx' (Tabela 10 tem dois blocos por linha)."""
    blocks, cur = [], None
    for it in row:
        txt = it["text"].replace(" ", "")
        if ROW_ID.match(txt):
            cur = [int(ROW_ID.match(txt).group(1)), []]
            blocks.append(cur)
        elif cur is not None:
            cur[1].append(it["text"])
    return blocks


def parse_table10(top: dict, bottom: dict) -> pd.DataFrame:
    """Tabela 10 (PDF p.63): bloco esquerdo = TR 10.000 anos; direito = TR 10 anos."""
    recs = []
    for src in (top, bottom):
        for row in rows_of(src["items"], tol=12):
            blocks = _split(row)
            if not blocks:
                continue
            if len(blocks) != 2:
                raise ValueError(f"linha com {len(blocks)} blocos ST: {[b[0] for b in blocks]}")
            for (sid, toks), tr in zip(blocks, ("10000", "10")):
                vals = [t for t in toks]
                if len(vals) == 7 and sid == 22:  # último campo é '-' (tempo da onda) e o OCR o descartou
                    vals.append("-")
                if len(vals) != 8:
                    raise ValueError(f"ST-{sid:02d} TR{tr}: {len(vals)} campos {vals}")
                v = {c: num(x, flow=(c == "vazao_max_m3s")) for c, x in zip(T10_COLS, vals)}
                v.update(secao=f"ST-{sid:02d}", tr_anos=int(tr), vazao_marcada_asterisco="*" in vals[5])
                recs.append(v)
    df = pd.DataFrame(recs)
    df = df.sort_values(["tr_anos", "secao"], ascending=[False, True]).reset_index(drop=True)
    return df[["secao", "tr_anos", *T10_COLS, "vazao_marcada_asterisco"]]


def parse_table9(src: dict) -> pd.DataFrame:
    """Tabela 9 (PDF p.62): cenário SEM ruptura. Formato longo: uma linha por seção × TR."""
    recs = []
    for row in rows_of(src["items"], tol=6):
        blocks = _split(row)
        if not blocks:
            continue
        if len(blocks) != 1:
            raise ValueError(f"linha com {len(blocks)} blocos ST")
        sid, toks = blocks[0]
        if sid == 0:  # velocidades são '-' e o OCR as descarta: dist, fundo, depois (prof, elev) x 5
            if len(toks) != 12:
                raise ValueError(f"ST-00: {len(toks)} campos {toks}")
            dist, fundo, rest = toks[0], toks[1], toks[2:]
            trip = [(rest[2 * i], None, rest[2 * i + 1]) for i in range(5)]
        else:
            if len(toks) != 17:
                raise ValueError(f"ST-{sid:02d}: {len(toks)} campos {toks}")
            dist, fundo, rest = toks[0], toks[1], toks[2:]
            trip = [(rest[3 * i], rest[3 * i + 1], rest[3 * i + 2]) for i in range(5)]
        for tr, (p, vel, el) in zip(T9_TR, trip):
            recs.append(dict(secao=f"ST-{sid:02d}", tr_anos=int(tr), distancia_km=num(dist), elev_fundo_m=num(fundo),
                             prof_max_m=num(p), vel_max_ms=(num(vel) if vel is not None else None), elev_max_m=num(el)))
    return pd.DataFrame(recs).sort_values(["tr_anos", "secao"]).reset_index(drop=True)


def crosscheck(a: pd.DataFrame, b: pd.DataFrame, keys=("secao", "tr_anos")) -> list[dict]:
    """Células em que duas leituras OCR (escalas distintas) discordam."""
    m = a.merge(b, on=list(keys), suffixes=("_a", "_b"))
    diffs = []
    for c in [c for c in a.columns if c not in keys and c in b.columns]:
        for _, r in m.iterrows():
            x, y = r[f"{c}_a"], r[f"{c}_b"]
            same = (pd.isna(x) and pd.isna(y)) or (not pd.isna(x) and not pd.isna(y) and abs(float(x) - float(y)) < 1e-9)
            if not same:
                diffs.append(dict(secao=r["secao"], tr_anos=int(r["tr_anos"]), coluna=c, leitura_a=x, leitura_b=y))
    return diffs
