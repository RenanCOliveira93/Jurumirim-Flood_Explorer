"""Figuras reproduzíveis (matplotlib) usadas por notebooks, exportações e vídeo."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from . import DISCLAIMER, data
from .terrain import DEM_PATH, hillshade
from .georef import CRS

COL = {"ZAS": "#d62728", "ZSS_APENAS": "#7fd62a", "ENVOLTORIA_RUPTURA": "#222222", "CHEIA_SR": "#1f5fd6"}
FOOT = "Fonte: " + data.SRC_TABLE + "\n" + DISCLAIMER


def footer(fig, extra=""):
    fig.text(0.01, 0.005, (extra + "\n" if extra else "") + FOOT, fontsize=6.5, color="#555", va="bottom")


def section_charts():
    s = data.sections()
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5), constrained_layout=True)
    spec = [("tempo_chegada_min", "Tempo de chegada (min)"), ("sobrelevacao_m", "Sobrelevação máxima (m)"),
            ("velocidade_ms", "Velocidade máxima (m/s)"), ("vazao_pico_m3s", "Vazão de pico (m³/s)")]
    for a, (c, t) in zip(ax.ravel(), spec):
        a.plot(s.distancia_km, s[c], "o-", color="#1f5fd6", ms=4)
        a.set_title(t, fontsize=10); a.set_xlabel("Distância da barragem (km)"); a.grid(alpha=.3)
        for _, r in s.iterrows():
            if r.id in ("ST-001", "ST-006", "ST-014", "ST-017") and not np.isnan(r[c]):
                a.annotate(r.id, (r.distancia_km, r[c]), fontsize=7, xytext=(3, 4), textcoords="offset points")
    ax[1, 1].set_yscale("log")
    fig.suptitle("Seções da onda — DADO OFICIAL (PAE, p. 38)", fontsize=12)
    footer(fig)
    return fig


def _dem_extent():
    with rasterio.open(DEM_PATH) as src:
        z = src.read(1).astype(float)
        b = src.bounds
        t = src.transform
    from pyproj import Transformer
    z[z < -100] = np.nan
    return z, b, t


def overview_map(zoom_urban=False, show_cheia=True, figsize=(11, 8.5)):
    """Mapa estático: hillshade + manchas + município + áreas urbanizadas + seções."""
    p = data.polygons()
    mun = data.municipios(); urb = data.urbanizadas(); pts = data.section_points()
    z, b, t = _dem_extent()
    from rasterio.warp import transform_bounds, reproject, Resampling
    # reprojeta hillshade para UTM
    xmin, ymin, xmax, ymax = 660000, 7428500, 686000, 7448000
    res = 30
    W, H = int((xmax - xmin) / res), int((ymax - ymin) / res)
    dst = np.full((H, W), np.nan, np.float32)
    from rasterio.transform import from_origin
    reproject(z.astype(np.float32), dst, src_transform=t, src_crs="EPSG:4326",
              dst_transform=from_origin(xmin, ymax, res, res), dst_crs=CRS, resampling=Resampling.bilinear,
              src_nodata=np.nan, dst_nodata=np.nan)
    hs = hillshade(dst, res, res)
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(dst, extent=(xmin, xmax, ymin, ymax), cmap="terrain", alpha=.55, zorder=0)
    ax.imshow(hs, extent=(xmin, xmax, ymin, ymax), cmap="gray", alpha=.35, zorder=1)
    mun[mun.nome.isin(["Piraju", "Cerqueira César", "Manduri", "Sarutaiá"])].boundary.plot(
        ax=ax, color="#555", lw=.8, ls="--", zorder=2)
    urb.plot(ax=ax, color="#ff9800", alpha=.55, zorder=3)
    for cl, kw in (("ZSS_APENAS", dict(fc=COL["ZSS_APENAS"], alpha=.55)), ("ZAS", dict(fc=COL["ZAS"], alpha=.55))):
        p[p.classe == cl].plot(ax=ax, ec="k", lw=.4, zorder=4, **{("color" if k == "fc" else k): v for k, v in kw.items()})
    if show_cheia:
        p[p.classe == "CHEIA_SR"].boundary.plot(ax=ax, color=COL["CHEIA_SR"], lw=.9, zorder=5)
    pts.plot(ax=ax, color="k", markersize=14, zorder=6)
    for _, r in pts.iterrows():
        ax.annotate(r.id[3:], (r.geometry.x, r.geometry.y), fontsize=6.5, xytext=(3, 3), textcoords="offset points", zorder=7)
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_aspect("equal")
    ax.set_xlabel("E UTM 22S (m)"); ax.set_ylabel("N UTM 22S (m)")
    ax.set_title("Mancha oficial do PAE (digitalizada) × Piraju — DERIVADO DO PAE", fontsize=11)
    ax.legend(handles=[
        Patch(fc=COL["ZAS"], alpha=.55, label="ZAS implantada (PAE)"),
        Patch(fc=COL["ZSS_APENAS"], alpha=.55, label="ZSS (PAE)"),
        Line2D([0], [0], color=COL["CHEIA_SR"], label="Cheia TR 10.000 sem ruptura (baixa confiança)"),
        Patch(fc="#ff9800", alpha=.55, label="Áreas urbanizadas IBGE 2019"),
        Line2D([0], [0], color="#555", ls="--", label="Limites municipais IBGE"),
        Line2D([0], [0], marker="o", color="k", ls="", ms=4, label="Seções ST (PAE)")], loc="lower left", fontsize=8)
    footer(fig, "Relevo: Copernicus GLO-30 (EGM2008). Limites: IBGE. Datum horizontal SIRGAS 2000 / UTM 22S.")
    fig.subplots_adjust(bottom=.1)
    return fig
