"""DEM Copernicus GLO-30 (EGM2008, ~30 m, MDS): amostragem, perfis e sombreamento.

Os perfis são DESCRITIVOS do terreno. Não é válido comparar cotas simples para
inferir alcance de inundação (ver docs/GUIA_TECNICO.md)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from shapely.geometry import LineString

from .georef import CRS, section_lines, utm_to_pt, pt_to_utm
from .paths import RAW

DEM_PATH = RAW / "copernicus_glo30_jurumirim_piraju.tif"
_to_wgs = Transformer.from_crs(CRS, "EPSG:4326", always_xy=True)


def sample_dem(e, n, dem_path=DEM_PATH):
    lon, lat = _to_wgs.transform(np.asarray(e, float), np.asarray(n, float))
    with rasterio.open(dem_path) as src:
        vals = np.array([v[0] for v in src.sample(zip(lon, lat))], float)
        nod = src.nodata
    if nod is not None:
        vals[vals == nod] = np.nan
    return vals


def section_geometries(A, sections_df, tol_m=10.0) -> dict[str, LineString]:
    """Associa os traços vetoriais de seção da prancha ao ID mais próximo (UTM)."""
    segs = section_lines()
    lines = {r.id: [] for r in sections_df.itertuples()}
    for x0, y0, x1, y1 in segs:
        (e0, e1), (n0, n1) = pt_to_utm(A, [x0, x1], [y0, y1])
        seg = LineString([(e0, n0), (e1, n1)])
        best = min(sections_df.itertuples(), key=lambda r: seg.distance(__import__("shapely").geometry.Point(r.x_utm, r.y_utm)))
        if seg.distance(__import__("shapely").geometry.Point(best.x_utm, best.y_utm)) < tol_m:
            lines[best.id].append(seg)
    out = {}
    for k, v in lines.items():
        if v:
            pts = [c for s in v for c in s.coords]
            # envolve por projeção ao longo do eixo principal
            arr = np.array(pts)
            d = arr - arr.mean(axis=0)
            u = np.linalg.svd(d, full_matrices=False)[2][0]
            order = np.argsort(d @ u)
            out[k] = LineString(arr[order][[0, -1]]) if len(arr) >= 2 else None
    return out


def profile(line: LineString, step_m=30.0) -> pd.DataFrame:
    n = max(int(line.length // step_m), 2)
    dist = np.linspace(0, line.length, n)
    pts = np.array([line.interpolate(d).coords[0] for d in dist])
    z = sample_dem(pts[:, 0], pts[:, 1])
    return pd.DataFrame({"dist_m": dist, "e": pts[:, 0], "n": pts[:, 1], "z_m": z})


def hillshade(z, cellx, celly, az=315, alt=45):
    z = np.where(np.isnan(z), np.nanmean(z), z)
    gy, gx = np.gradient(z, celly, cellx)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    azr, altr = np.radians(360 - az + 90), np.radians(alt)
    hs = np.sin(altr) * np.sin(slope) + np.cos(altr) * np.cos(slope) * np.cos(azr - aspect)
    return np.clip(hs, 0, 1)
