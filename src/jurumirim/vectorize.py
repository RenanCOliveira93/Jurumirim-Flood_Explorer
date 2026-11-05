"""Vetorização por cor das manchas da prancha p. 38 (raster -> polígonos UTM).

Não é uma extração vetorial nativa: o mapa do PDF é raster. As linhas de contorno
têm cores exatas (legenda): ZAS vermelho (255,0,0), ZSS verde (75,230,0) e cheia de
projeto sem ruptura azul (0,92,230). Cada classe é segmentada por distância de cor,
as lacunas (rótulos/ícones sobrepostos) são fechadas morfologicamente, o interior
é preenchido e o contorno é convertido para UTM pela transformação da grade.
"""
from __future__ import annotations

import cv2
import geopandas as gpd
import numpy as np
import pymupdf
from scipy.ndimage import convolve
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize
from shapely.geometry import Polygon
from shapely.validation import make_valid

from .georef import CRS, MAP_FRAME, fit_transform
from .paths import PDF

ZOOM = 3.0
CLASSES = {
    "ZAS": {"rgb": (255, 0, 0), "desc": "Zona de Autossalvamento (ZAS) Implantada"},
    "ZSS": {"rgb": (75, 230, 0), "desc": "Zona de Segurança Secundária (ZSS) — envoltória externa"},
    "CHEIA_SR": {"rgb": (0, 92, 230), "desc": "Cheia de projeto TR=10.000 anos, sem ruptura"},
}
# região da prancha ocupada pela tabela de seções (sobreposta ao mapa), em pt
TABLE_RECT = (1007, 135, 1750, 710)


def render_map(pdf_path=PDF, zoom=ZOOM):
    page = pymupdf.open(pdf_path)[37]
    clip = pymupdf.Rect(*MAP_FRAME)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy()
    return img


# faixas HSV (OpenCV: H 0-180) derivadas das cores exatas da legenda
HSV_RANGES = {
    "ZAS": [((0, 200, 190), (5, 255, 255)), ((175, 200, 190), (180, 255, 255))],
    "ZSS": [((44, 150, 160), (58, 255, 255))],
    "CHEIA_SR": [((105, 130, 150), (116, 255, 255))],
}


def color_mask(img, name_or_rgb, tol=45):
    if isinstance(name_or_rgb, str):
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        m = np.zeros(img.shape[:2], np.uint8)
        for lo, hi in HSV_RANGES[name_or_rgb]:
            m |= cv2.inRange(hsv, np.array(lo), np.array(hi)) > 0
        m = m.astype(np.uint8)
    else:
        d = np.sqrt(((img.astype(np.int32) - np.array(name_or_rgb)) ** 2).sum(axis=2))
        m = (d < tol).astype(np.uint8)
    # exclui a região da tabela
    x0, y0, x1, y1 = [(v - o) * ZOOM for v, o in zip(TABLE_RECT, (MAP_FRAME[0], MAP_FRAME[1]) * 2)]
    m[int(max(y0, 0)):int(y1), int(max(x0, 0)):int(x1)] = 0
    return m


def bridge_gaps(mask, radius_px=90, pre_close=7, iters=3):
    """Fecha lacunas da linha: esqueleto + ligação de pontas livres ao esqueleto
    de OUTRO componente dentro de ``radius_px`` (rótulos/ícones sobrepostos
    interrompem as linhas). Retorna (esqueleto, estatística)."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pre_close, pre_close))
    m = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    sk = skeletonize(m > 0).astype(np.uint8)
    stats = {"pontas_iniciais": None, "pontes": 0, "pontas_restantes": 0}
    for it in range(iters):
        nb = convolve(sk, np.ones((3, 3)), mode="constant") - sk
        ends = np.argwhere((sk == 1) & (nb == 1))
        if stats["pontas_iniciais"] is None:
            stats["pontas_iniciais"] = int(len(ends))
        _, lab = cv2.connectedComponents(sk, connectivity=8)
        pts = np.argwhere(sk > 0)
        tree = cKDTree(pts)
        added = 0
        for y, x in ends:
            best, bd = None, 1e9
            for i in tree.query_ball_point((y, x), radius_px):
                py, px = pts[i]
                if lab[py, px] == lab[y, x]:
                    continue
                d = np.hypot(py - y, px - x)
                if d < bd:
                    bd, best = d, (py, px)
            if best is not None:
                cv2.line(sk, (int(x), int(y)), (int(best[1]), int(best[0])), 1, 1)
                added += 1
        stats["pontes"] += added
        sk = skeletonize(cv2.dilate(sk, np.ones((3, 3), np.uint8)) > 0).astype(np.uint8)
        if added == 0:
            break
    nb = convolve(sk, np.ones((3, 3)), mode="constant") - sk
    stats["pontas_restantes"] = int(((sk == 1) & (nb == 1)).sum())
    return sk, stats


def filled_regions(line_mask):
    """Preenche o interior de contornos fechados (tudo que não é fundo ligado à borda)."""
    h, w = line_mask.shape
    pad = cv2.copyMakeBorder(line_mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    ff = pad.copy()
    cv2.floodFill(ff, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 2)
    return ((ff != 2).astype(np.uint8))[1:-1, 1:-1]


def line_half_width_px(mask):
    dt = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    vals = dt[mask > 0]
    return float(np.percentile(vals, 90)) if vals.size else 0.0


def _contours_to_polys(filled, A, min_area_m2):
    contours, hier = cv2.findContours(filled, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for i, c in enumerate(contours):
        if len(c) < 4:
            continue
        pts = c[:, 0, :].astype(float)
        px = MAP_FRAME[0] + (pts[:, 0] + 0.5) / ZOOM
        py = MAP_FRAME[1] + (pts[:, 1] + 0.5) / ZOOM
        e = A[0, 0] * px + A[0, 1] * py + A[0, 2]
        n = A[1, 0] * px + A[1, 1] * py + A[1, 2]
        polys.append((hier[0][i][3], Polygon(np.c_[e, n])))
    outer = [p for parent, p in polys if parent < 0 and p.area > min_area_m2]
    holes = [p for parent, p in polys if parent >= 0 and p.area > min_area_m2]
    out = []
    for p in outer:
        hs = [h.exterior.coords for h in holes if p.contains(h.representative_point())]
        out.append(make_valid(Polygon(p.exterior.coords, hs).simplify(2.5)))
    return out


def vectorize(pdf_path=PDF, min_area_m2=20000):
    """Retorna (GeoDataFrame, qualidade, imagem). Classes: ZAS, ZSS_CONTORNO,
    ENVOLTORIA_RUPTURA (união ZAS+ZSS), ZSS_APENAS (envoltória − ZAS), CHEIA_SR."""
    A, info = fit_transform(pdf_path)
    img = render_map(pdf_path)
    filled_by, quality = {}, {}
    mpp = info["scale_x_m_per_pt"] / ZOOM
    for name in CLASSES:
        mask = color_mask(img, name)
        sk, st = bridge_gaps(mask)
        line = cv2.dilate(sk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        filled_by[name] = filled_regions(line)
        quality[name] = {**st, "pixels_linha": int(mask.sum()), "m_por_pixel": mpp}
    geoms = {n: _contours_to_polys(f, A, min_area_m2) for n, f in filled_by.items()}
    rows = []
    for n, gl in geoms.items():
        for g in gl:
            rows.append({"classe": n, "descricao": CLASSES[n]["desc"], "geometry": g})
    gdf = gpd.GeoDataFrame(rows, crs=CRS)
    # derivados (união em CRS projetado)
    zas = gdf[gdf.classe == "ZAS"].geometry.union_all()
    zss = gdf[gdf.classe == "ZSS"].geometry.union_all()
    env = make_valid(zas.union(zss).buffer(8).buffer(-8))  # funde junção ZAS|ZSS
    zss_only = make_valid(env.difference(zas))
    extra = gpd.GeoDataFrame([
        {"classe": "ENVOLTORIA_RUPTURA", "descricao": "Derivado: união ZAS ∪ ZSS (envoltória de ruptura hipotética)", "geometry": env},
        {"classe": "ZSS_APENAS", "descricao": "Derivado: envoltória − ZAS", "geometry": zss_only},
    ], crs=CRS)
    gdf = gpd.GeoDataFrame(__import__("pandas").concat([gdf, extra], ignore_index=True), crs=CRS)
    gdf["area_km2"] = gdf.geometry.area / 1e6
    gdf["valido"] = gdf.geometry.is_valid
    gdf["origem"] = "vetorização por cor da prancha raster p.38; ver data/metadata/pae_provenance.json"
    return gdf, quality, img
