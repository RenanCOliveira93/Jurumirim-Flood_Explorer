#!/usr/bin/env python
"""OCR das imagens embutidas do PAE UHE Piraju (Tabelas 9/10 e Figura 17) -> JSON bruto versionável.

Dependência OPCIONAL (fora do requirements.txt): `pip install rapidocr-onnxruntime pymupdf`.
O restante do pipeline (scripts/build_dams.py) lê só os JSON gerados aqui; sem este script o dataset
já versionado continua utilizável. Cada tabela é lida em duas escalas para checagem cruzada.
"""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "PAE-UHE-Piraju.pdf"
OUT = ROOT / "data" / "processed" / "dams" / "PIR" / "ocr_raw"
# (nome, página física 1-based, seleção da imagem, escalas)
JOBS = [
    ("fig17", 61, "largest", (1.0,)),
    ("tabela9", 62, "largest", (2.0, 3.0)),
    ("tabela10_top", 63, "first_wide", (1.0, 1.5)),
    ("tabela10_bottom", 63, "second_wide", (1.0, 1.5)),
]


def image_of(doc, page_no, which):
    imgs = []
    for im in doc[page_no - 1].get_images(full=True):
        pix = pymupdf.Pixmap(doc, im[0])
        if pix.n > 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        imgs.append((im[0], pix))
    if which == "largest":
        xref, pix = max(imgs, key=lambda t: t[1].width * t[1].height)
    else:
        wide = sorted([t for t in imgs if t[1].width > 2500], key=lambda t: t[0])
        xref, pix = wide[0 if which == "first_wide" else 1]
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return xref, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(PDF.read_bytes()).hexdigest()
    ocr = RapidOCR()
    with pymupdf.open(PDF) as doc:
        for name, page, which, scales in JOBS:
            xref, img = image_of(doc, page, which)
            cv2.imwrite(str(OUT / f"{name}.png"), img)
            for sc in scales:
                big = img if sc == 1 else cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
                res, _ = ocr(big)
                items = []
                for box, text, conf in res or []:
                    xs = [p[0] for p in box]; ys = [p[1] for p in box]
                    items.append(dict(text=text, conf=round(float(conf), 3), x0=round(min(xs) / sc, 1),
                                      x1=round(max(xs) / sc, 1), y0=round(min(ys) / sc, 1), y1=round(max(ys) / sc, 1)))
                meta = dict(source_document="PAE UHE Piraju 3308-HID-CBA-A-RT-G00-0001", source_pdf_sha256=sha,
                            pdf_page=page, image_xref=xref, image_size=[img.shape[1], img.shape[0]], scale=sc,
                            engine="rapidocr-onnxruntime", generated_on=str(date.today()), items=items)
                (OUT / f"{name}_s{sc:g}.json").write_text(json.dumps(meta, ensure_ascii=False))
                print(f"{name} s{sc:g}: {len(items)} caixas")


if __name__ == "__main__":
    sys.exit(main())
