"""Georreferenciamento da prancha p. 38 a partir da grade UTM vetorial do PDF.

As 6 linhas verticais e 6 horizontais cinzas (cor 0.43) da grade são desenhadas
no PDF em posições exatas; os rótulos (667000...682000 / 7431000...7446000)
as identificam. A transformação página(pt) -> UTM 22S (EPSG:31982) é ajustada
por mínimos quadrados e o RMS é reportado. Checagem independente: o ponto
central de cada seção ST-xxx deve cair sobre o traço da seção na prancha.
"""
from __future__ import annotations

import re

import numpy as np
import pymupdf

from .paths import PDF

PAGE = 38
CRS = "EPSG:31982"
GRID_COLOR = (0.43, 0.43, 0.43)
MAP_FRAME = (42.479, 42.721, 1762.397, 1641.658)  # x0, y0, x1, y1 (pt)


def _grid(page):
    xs, ys = [], []
    for d in page.get_drawings():
        if d["color"] and tuple(round(c, 2) for c in d["color"]) == GRID_COLOR:
            r = d["rect"]
            if abs(r.x1 - r.x0) < 1e-3 and r.height > 1000:
                xs.append(r.x0)
            elif abs(r.y1 - r.y0) < 1e-3 and r.width > 1000:
                ys.append(r.y0)
    labels_x = sorted({int(w[4]) for w in page.get_text("words") if re.fullmatch(r"6\d{5}", w[4])})
    labels_y = sorted({int(w[4]) for w in page.get_text("words") if re.fullmatch(r"74\d{5}", w[4])})
    return sorted(xs), sorted(ys, reverse=True), labels_x, sorted(labels_y)


def fit_transform(pdf_path=PDF):
    """Retorna (A, info): A é matriz afim 2x3 pt->UTM e info o dicionário de qualidade."""
    page = pymupdf.open(pdf_path)[PAGE - 1]
    gx, gy, lx, ly = _grid(page)
    gy = sorted(gy)  # y crescente em pt = norte decrescente
    ly = sorted(ly, reverse=True)
    if not (len(gx) == len(lx) == 6 and len(gy) == len(ly) == 6):
        raise RuntimeError("grade UTM não identificada")
    pts, utm = [], []
    for px, ex in zip(gx, lx):
        for py, ny in zip(gy, ly):
            pts.append((px, py)); utm.append((ex, ny))
    pts, utm = np.array(pts), np.array(utm, float)
    M = np.c_[pts, np.ones(len(pts))]
    coef, *_ = np.linalg.lstsq(M, utm, rcond=None)  # 3x2
    res = M @ coef - utm
    rms = float(np.sqrt((res ** 2).sum(axis=1).mean()))
    A = coef.T  # 2x3
    info = {
        "n_control_points": len(pts),
        "rms_m": rms,
        "max_residual_m": float(np.abs(res).max()),
        "scale_x_m_per_pt": float(abs(A[0, 0])),
        "scale_y_m_per_pt": float(abs(A[1, 1])),
        "crs": CRS,
        "control_points": "interseções das 12 linhas de grade UTM vetoriais (PDF p.38)",
    }
    return A, info


def pt_to_utm(A, x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return A[0, 0] * x + A[0, 1] * y + A[0, 2], A[1, 0] * x + A[1, 1] * y + A[1, 2]


def utm_to_pt(A, e, n):
    L = A[:, :2]
    inv = np.linalg.inv(L)
    d = inv @ np.vstack([np.asarray(e, float) - A[0, 2], np.asarray(n, float) - A[1, 2]])
    return d[0], d[1]


def section_lines(pdf_path=PDF):
    """Traços das seções ST (linhas pretas largura 1.6) em pt."""
    page = pymupdf.open(pdf_path)[PAGE - 1]
    segs = []
    for d in page.get_drawings():
        if d["color"] and tuple(round(c, 2) for c in d["color"]) == (0, 0, 0) and abs((d["width"] or 0) - 1.6) < 0.05:
            for it in d["items"]:
                if it[0] == "l":
                    segs.append((it[1].x, it[1].y, it[2].x, it[2].y))
    return segs


def _dist_point_segments(px, py, segs):
    best = np.inf
    for x0, y0, x1, y1 in segs:
        vx, vy = x1 - x0, y1 - y0
        L2 = vx * vx + vy * vy
        t = 0 if L2 == 0 else max(0, min(1, ((px - x0) * vx + (py - y0) * vy) / L2))
        best = min(best, np.hypot(px - (x0 + t * vx), py - (y0 + t * vy)))
    return best


def independent_check(A, sections_df, segs):
    """Distância (m) do ponto central tabelado ao traço de seção mais próximo."""
    out = {}
    for _, r in sections_df.iterrows():
        px, py = utm_to_pt(A, r.x_utm, r.y_utm)
        d_pt = _dist_point_segments(float(px[0]), float(py[0]), segs)
        out[r.id] = d_pt * float(abs(A[0, 0]))
    return out
