"""ESTIMATIVA EXPLORATÓRIA de mancha: relevo (Copernicus GLO-30) preenchido até a cota máxima TABELADA no PAE.

NÃO é simulação hidráulica nem resultado do PAE. Para cada seção o PAE dá a cota máxima da água; interpolamos essa
cota linearmente ao longo do rio (km) e marcamos as células do relevo que ficam abaixo dela e conectadas ao rio.
Limites que o usuário precisa ver junto com qualquer número daqui:
  * o MDS inclui vegetação/edificações e tem erro vertical de metros; resolução ~30 m;
  * a posição das seções de Piraju é ILUSTRATIVA (km sobre o eixo OSM, ±centenas de m);
  * a cota do PAE e a do DEM podem ter referenciais verticais diferentes (EGM2008 × datum local);
  * não há dinâmica (inércia, volume, tempo): é um 'enchimento' estático.
A qualidade é medida contra a mancha clara da Figura 17 do PAE Piraju (cenário SEM ruptura): ver `validate_natural`.
"""
from __future__ import annotations

import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.warp import Resampling, calculate_default_transform, reproject
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

from . import dams as D
from . import paths, riverpos

CRS = "EPSG:31982"
RES = 30.0
CORRIDOR_M = 1500.0  # só células a até 1,5 km do eixo do rio entram (evita vazar para outras calhas)
SEED_M = 90.0        # células a até 90 m do eixo servem de semente de conectividade

_DEM_CACHE: dict = {}


def _dem_utm():
    """DEM reprojetado para UTM 22S (30 m). Devolve (array float32, transform)."""
    if "dem" in _DEM_CACHE:
        return _DEM_CACHE["dem"]
    src_path = paths.RAW / "copernicus_glo30_jurumirim_piraju.tif"
    with rasterio.open(src_path) as src:
        tr, w, h = calculate_default_transform(src.crs, CRS, src.width, src.height, *src.bounds, resolution=RES)
        dst = np.full((h, w), np.nan, dtype="float32")
        reproject(rasterio.band(src, 1), dst, src_transform=src.transform, src_crs=src.crs, dst_transform=tr,
                  dst_crs=CRS, resampling=Resampling.bilinear, dst_nodata=np.nan)
    _DEM_CACHE["dem"] = (dst, tr)
    return dst, tr


def _downstream_line(dam: str = "PIR", length_km: float = 33.0) -> LineString:
    river = riverpos.river_line(paths.RAW / "osm_waterways.json")
    p = D.dam_points().set_index("dam").loc[dam]
    s0 = river.project(Point(p.x_utm, p.y_utm))
    end = min(river.length, s0 + length_km * 1000)
    ss = np.arange(s0, end, 25.0)
    return LineString([river.interpolate(s).coords[0] for s in ss])


def fill_to_profile(km_pts: np.ndarray, z_pts: np.ndarray, max_km: float | None = None, dam: str = "PIR"):
    """Células do DEM abaixo do perfil de cota Z(km) e conectadas ao eixo do rio. Retorna (máscara, transform, dem)."""
    dem, tr = _dem_utm()
    line = _downstream_line(dam)
    pts = np.array(line.coords)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))] / 1000.0  # km ao longo do eixo
    order = np.argsort(km_pts)
    z_along = np.interp(seg, np.asarray(km_pts)[order], np.asarray(z_pts)[order])  # sem extrapolar além das pontas (clamp)
    h, w = dem.shape
    cols, rows = np.meshgrid(np.arange(w), np.arange(h))
    xs, ys = rasterio.transform.xy(tr, rows, cols, offset="center")
    xs, ys = np.asarray(xs).reshape(h, w), np.asarray(ys).reshape(h, w)
    tree = cKDTree(pts)
    dist, idx = tree.query(np.c_[xs.ravel(), ys.ravel()])
    dist, idx = dist.reshape(h, w), idx.reshape(h, w)
    z = z_along[idx]
    ok = (dist <= CORRIDOR_M) & np.isfinite(dem)
    # células ATRÁS do eixo da barragem (a montante) não fazem parte do enchimento a jusante
    d0 = pts[1] - pts[0]
    behind = (idx == 0) & (((xs - pts[0, 0]) * d0[0] + (ys - pts[0, 1]) * d0[1]) < 0)
    ok &= ~behind
    if max_km is not None:
        ok &= seg[idx] <= max_km
    wet = ok & (dem <= z)
    lab, n = ndi.label(wet)
    seeds = np.unique(lab[wet & (dist <= SEED_M)])
    seeds = seeds[seeds > 0]
    mask = np.isin(lab, seeds)
    # suaviza a borda, mas só aceita células que de fato ficam abaixo da cota (o fechamento sozinho acrescentava ~0,6 % acima dela)
    mask = ndi.binary_closing(mask, iterations=1) & ok & (dem <= z)
    return mask, tr, dem, seg[idx]


def polygon_from_mask(mask: np.ndarray, tr) -> "shapely.geometry.base.BaseGeometry":
    geoms = [shape(g) for g, v in shapes(mask.astype("uint8"), mask=mask, transform=tr) if v == 1]
    return unary_union(geoms).simplify(RES / 2) if geoms else Point(0, 0).buffer(0)


def profile(kind: str, tr_anos: int) -> tuple[np.ndarray, np.ndarray]:
    """(km, cota máx.) tabelados no PAE de Piraju. kind: 'ruptura' (Tabela 10) ou 'natural' (Tabela 9). Exclui ST-00 (montante)."""
    if kind == "ruptura":
        s = D.sections("PIR", {10000: "ruptura_tr10000", 10: "ruptura_tr10"}[tr_anos])
    else:
        s = D.natural_sections(tr_anos).rename(columns={})
    s = s[s.secao != "ST-00"].dropna(subset=["elev_max_m"])
    return s.distancia_km.to_numpy(float), s.elev_max_m.to_numpy(float)


def estimate(kind: str = "ruptura", tr_anos: int = 10000, max_km: float | None = None):
    km, z = profile(kind, tr_anos)
    mask, tr, dem, kmcell = fill_to_profile(km, z, max_km)
    return polygon_from_mask(mask, tr), mask, tr, kmcell


def zas_stretch(dam: str, km: float) -> LineString:
    """Trecho de rio de `km` quilômetros a jusante da barragem (eixo OSM): a ZAS oficial é DEFINIDA por extensão (km),
    então desenhamos o trecho, não uma área. Posição ILUSTRATIVA (eixo OSM)."""
    return _downstream_line(dam, km)
