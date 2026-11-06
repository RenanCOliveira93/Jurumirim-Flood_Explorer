#!/usr/bin/env python
"""Gera os visuais 'estilo drone': mapas de relevo sombreado (docs/img) e vídeos (outputs/). Rótulos e limites: ver terrain3d.py."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jurumirim import terrain3d as T  # noqa: E402

what = sys.argv[1:] or ["maps", "orbita", "frente_piraju", "frente_jurumirim"]
img, out = ROOT / "docs" / "img", ROOT / "outputs"
img.mkdir(parents=True, exist_ok=True)
if "maps" in what:
    for k, show in (("piraju", ("pir",)), ("corredor", ("jur", "pir")), ("paranapanema", ("pir",))):
        T.map_figure(k, show).savefig(img / f"relevo_{k}.png", dpi=110, bbox_inches="tight")
    T.frame_3d("piraju", None, -40, show=("pir",)).savefig(img / "3d_piraju.png", dpi=110, bbox_inches="tight")
    T.frame_3d("corredor", None, -85, elev=48, show=("jur", "pir"), figsize=(13, 7)).savefig(img / "3d_corredor.png", dpi=110, bbox_inches="tight")
    print("mapas ok")
if "orbita" in what:
    print(T.export_video(T.orbit_frames("piraju", 72), out / "drone_orbita_piraju.mp4"))
if "frente_piraju" in what:
    print(T.export_video(T.front_frames("piraju", ("pir",), 80), out / "drone_frente_piraju.mp4"))
if "frente_jurumirim" in what:
    print(T.export_video(T.front_frames("corredor", ("jur",), 80), out / "drone_frente_jurumirim.mp4"))
