"""Georreferenciamento da Figura 17 do PAE Piraju (seções ST-xx) pelas cruzes da grade UTM.

A figura é raster (1139x782 px, ~18 m/px). Pontos de controle = cruzes pretas nos cruzamentos de
coordenadas rotuladas nos eixos. Os rótulos ST-xx vêm do OCR (ST-08 lido como '80-15'; correção
conferida visualmente na imagem e registrada em ST08_FIX).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

GRID_E = [654000, 658000, 662000, 666000, 670000]
GRID_N = [7442000, 7438000, 7434000]
ST08_FIX = re.compile(r"80[-–]?15")  # OCR leu 'ST-08' como '80-15'; posição conferida na figura


def axis_guess(items: list[dict]) -> tuple[list[float], list[float]]:
    """Posições aproximadas (px) dos rótulos de coordenada: E no eixo inferior, N no direito."""
    xs, ys = {}, {}
    for it in items:
        t = it["text"].replace(" ", "")
        cx, cy = (it["x0"] + it["x1"]) / 2, (it["y0"] + it["y1"]) / 2
        if t.isdigit() and len(t) == 6 and int(t) in GRID_E:
            xs[int(t)] = cx
        if t.isdigit() and len(t) == 7 and int(t) in GRID_N:
            ys[int(t)] = cy
    if len(xs) != len(GRID_E) or len(ys) != len(GRID_N):
        raise ValueError(f"rótulos de eixo incompletos: E={sorted(xs)} N={sorted(ys)}")
    return [xs[e] for e in GRID_E], [ys[n] for n in GRID_N]


def find_cross(gray: np.ndarray, cx: float, cy: float, r: int = 9, arm: int = 6):
    """Centro da cruz '+' escura mais provável em torno de (cx, cy): (score, (x, y)). Braços mais escuros que os lados."""
    cx, cy = int(round(cx)), int(round(cy))
    best = (-1e9, None)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            x, y = cx + dx, cy + dy
            if x - arm < 0 or y - arm < 0 or x + arm >= gray.shape[1] or y + arm >= gray.shape[0]:
                continue
            horiz, vert = gray[y, x - arm:x + arm + 1].mean(), gray[y - arm:y + arm + 1, x].mean()
            side = (gray[y - 2, x - arm:x + arm + 1].mean() + gray[y + 2, x - arm:x + arm + 1].mean()
                    + gray[y - arm:y + arm + 1, x - 2].mean() + gray[y - arm:y + arm + 1, x + 2].mean()) / 4
            score = side - (horiz + vert) / 2
            if score > best[0]:
                best = (score, (x, y))
    return best


def georef(image_gray: np.ndarray, ocr_items: list[dict], min_score: float = 8.0) -> dict:
    """Ajusta afim px->UTM 22S nas cruzes detectadas; devolve A, RMS, pontos usados e posição dos rótulos ST."""
    gx, gy = axis_guess(ocr_items)
    src, dst, used = [], [], []
    for j, n in enumerate(GRID_N):
        for i, e in enumerate(GRID_E):
            score, pos = find_cross(image_gray, gx[i], gy[j])
            # descarta candidatos ocultos por rótulos (score alto demais = borda de caixa) ou sem cruz (score baixo)
            if pos is not None and min_score <= score <= 45 and abs(pos[0] - gx[i]) <= 3 and abs(pos[1] - gy[j]) <= 3:
                src.append([pos[0], pos[1], 1.0]); dst.append([e, n]); used.append(dict(E=e, N=n, px=pos, score=round(score, 1)))
    if len(src) < 8:
        raise ValueError(f"poucas cruzes detectadas ({len(src)})")
    A, *_ = np.linalg.lstsq(np.array(src), np.array(dst, float), rcond=None)
    res = np.array(src) @ A - np.array(dst, float)
    rms = float(np.sqrt((res ** 2).sum(1).mean()))
    labels = {}
    for it in ocr_items:
        t = it["text"].replace(" ", "")
        m = re.fullmatch(r"ST[-–]?(\d{2})", t)
        sid = int(m.group(1)) if m else (8 if ST08_FIX.fullmatch(t) else None)
        if sid is not None:
            px, py = (it["x0"] + it["x1"]) / 2, (it["y0"] + it["y1"]) / 2
            e, n = np.array([px, py, 1.0]) @ A
            labels[f"ST-{sid:02d}"] = dict(px=[round(px, 1), round(py, 1)], x_utm=round(float(e), 1), y_utm=round(float(n), 1))
    return dict(affine=A.tolist(), rms_m=round(rms, 2), max_residual_m=round(float(np.hypot(*res.T).max()), 2),
                n_control_points=len(src), pixel_size_m=round(float(np.hypot(*A[0])), 2), control_points=used,
                labels=labels, st08_ocr_fix="rótulo lido como '80-15' (OCR) atribuído a ST-08 por posição, conferido visualmente")
