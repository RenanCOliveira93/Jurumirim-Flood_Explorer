"""Visuais estilo 'mapeamento por drone': relevo sombreado, 3D e frente da água avançando sobre o terreno.

Rótulos obrigatórios nas imagens: relevo = MDS Copernicus GLO-30 (30 m, inclui vegetação), EXAGERO VERTICAL declarado;
água de Piraju = ESTIMATIVA EXPLORATÓRIA (relevo até a cota do PAE); água de Jurumirim = mancha OFICIAL do PAE (p. 38);
avanço no tempo = INTERPOLAÇÃO ILUSTRATIVA entre tempos tabelados. Nada aqui é simulação hidráulica.
"""
from __future__ import annotations

import subprocess
import tempfile
import textwrap
from functools import lru_cache
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LightSource, LinearSegmentedColormap
from rasterio.features import rasterize
from scipy.spatial import cKDTree

from . import DISCLAIMER
from . import bathtub as B
from . import dams as D
from . import data, paths

REGIONS = {
    "piraju": dict(label="Cidade de Piraju e vale a jusante da barragem", bounds=(661500, 7432500, 669500, 7440200), step=1),
    "corredor": dict(label="Corredor Jurumirim → Piraju (≈ 33 km)", bounds=(653500, 7429500, 683500, 7442500), step=3, zoom=2.1),
    "paranapanema": dict(label="UHE Paranapanema e os 10 km de ZAS", bounds=(659000, 7431500, 667500, 7437500), step=1),
}
HYPSO = LinearSegmentedColormap.from_list("hypso", ["#1b5e3b", "#4c9a4f", "#bcd479", "#f2e394", "#d9a65f", "#a9743f", "#8a6a55", "#f5f0ea"])
WATER_PIR, WATER_JUR, WATER_NORMAL, URBAN = "#8e24aa", "#d62728", "#2aa9e0", "#ff7a00"
EXAG = 4.0


@lru_cache(maxsize=1)
def _dem():
    return B._dem_utm()


def window(key: str):
    """Recorte do DEM (UTM 22S). Retorna dict(z, x, y, sl=(slice_row, slice_col), tr)."""
    dem, tr = _dem()
    x0, y0, x1, y1 = REGIONS[key]["bounds"]
    c0, r1 = [int(v) for v in ~tr * (x0, y0)]
    c1, r0 = [int(v) for v in ~tr * (x1, y1)]
    r0, r1 = sorted((max(r0, 0), min(r1, dem.shape[0])))
    c0, c1 = sorted((max(c0, 0), min(c1, dem.shape[1])))
    sl = (slice(r0, r1), slice(c0, c1))
    z = dem[sl].astype(float)
    cols, rows = np.meshgrid(np.arange(c0, c1), np.arange(r0, r1))
    xs, ys = tr * (cols + .5, rows + .5)
    return dict(z=z, x=np.asarray(xs), y=np.asarray(ys), sl=sl, tr=tr)


def extremes(w: dict) -> dict:
    z = w["z"]
    hi, lo = np.unravel_index(np.nanargmax(z), z.shape), np.unravel_index(np.nanargmin(z), z.shape)
    return dict(alto=(float(w["x"][hi]), float(w["y"][hi]), float(z[hi])), baixo=(float(w["x"][lo]), float(w["y"][lo]), float(z[lo])))


# ---------------------------------------------------------------- camadas de água
@lru_cache(maxsize=4)
def _pir_estimate(tr_anos: int = 10000):
    """Máscara na grade do DEM, km de cada célula, cota da água por célula e tempo de chegada por célula (ILUSTRAÇÃO)."""
    km, zc = B.profile("ruptura", tr_anos)
    mask, tr, dem, kmcell = B.fill_to_profile(km, zc)
    s = D.sections("PIR", {10000: "ruptura_tr10000", 10: "ruptura_tr10"}[tr_anos])
    s = s[(s.secao != "ST-00")].dropna(subset=["t_frente_min"]).sort_values("distancia_km")
    t_arr = np.interp(kmcell, s.distancia_km.to_numpy(float), s.t_frente_min.to_numpy(float))
    z_water = np.interp(kmcell, np.sort(km), zc[np.argsort(km)])
    return dict(mask=mask, km=kmcell, t_arr=np.where(mask, t_arr, np.nan), z_water=np.where(mask, z_water, np.nan))


@lru_cache(maxsize=1)
def _jur_official():
    """Mancha OFICIAL (envoltória, PAE p. 38) rasterizada na grade do DEM; tempo de chegada por célula via seção mais próxima (ILUSTRAÇÃO)."""
    dem, tr = _dem()
    mask = rasterize([(data.envelope(), 1)], out_shape=dem.shape, transform=tr, fill=0, dtype="uint8").astype(bool)
    rx, ry = D.river_xy()
    seg = np.r_[0, np.cumsum(np.hypot(np.diff(rx), np.diff(ry)))] / 1000.0
    cols, rows = np.meshgrid(np.arange(dem.shape[1]), np.arange(dem.shape[0]))
    xs, ys = tr * (cols + .5, rows + .5)
    idx = cKDTree(np.c_[rx, ry]).query(np.c_[np.asarray(xs).ravel(), np.asarray(ys).ravel()])[1].reshape(dem.shape)
    s = D.sections("JUR").dropna(subset=["t_frente_min"]).sort_values("distancia_km")
    t_arr = np.interp(seg[idx], s.distancia_km.to_numpy(float), s.t_frente_min.to_numpy(float))
    return dict(mask=mask, t_arr=np.where(mask, t_arr, np.nan))


@lru_cache(maxsize=1)
def _normal_water():
    """Água atual (OSM) rasterizada na grade do DEM: referência 'situação normal'."""
    from . import gis
    dem, tr = _dem()
    g = gis.load_water()
    return rasterize([(geom, 1) for geom in g.geometry], out_shape=dem.shape, transform=tr, fill=0, dtype="uint8").astype(bool)


@lru_cache(maxsize=1)
def _urban():
    """Áreas urbanizadas IBGE 2019 rasterizadas na grade do DEM (≠ perímetro urbano legal)."""
    from . import gis
    dem, tr = _dem()
    return rasterize([(g, 1) for g in gis.load_urbanizadas().geometry], out_shape=dem.shape, transform=tr, fill=0, dtype="uint8").astype(bool)


def layers(w: dict, which=("jur", "pir", "normal")) -> dict:
    sl = w["sl"]
    out = {}
    if "jur" in which:
        j = _jur_official(); out["jur"] = dict(mask=j["mask"][sl], t_arr=j["t_arr"][sl])
    if "pir" in which:
        p = _pir_estimate(10000); out["pir"] = dict(mask=p["mask"][sl], t_arr=p["t_arr"][sl], z_water=p["z_water"][sl])
    if "normal" in which:
        out["normal"] = dict(mask=_normal_water()[sl])
    out["urban"] = dict(mask=_urban()[sl])
    return out


# ---------------------------------------------------------------- 2D: relevo sombreado
def shaded_rgb(w: dict, exag: float = EXAG) -> np.ndarray:
    z = np.where(np.isfinite(w["z"]), w["z"], np.nanmin(w["z"]))
    ls = LightSource(azdeg=315, altdeg=38)
    return ls.shade(z, cmap=HYPSO, blend_mode="soft", vert_exag=exag, dx=30, dy=30, vmin=np.nanpercentile(z, 1), vmax=np.nanpercentile(z, 99))[..., :3]


def _blend(rgb, mask, color, a):
    c = np.array(plt.matplotlib.colors.to_rgb(color))
    out = rgb.copy(); out[mask] = (1 - a) * out[mask] + a * c
    return out


def map_figure(key: str, show=("jur", "pir"), figsize=(11, 8)):
    """Mapa de relevo sombreado com marcação do ponto mais alto e do mais baixo e, opcionalmente, as manchas."""
    w = window(key); L = layers(w, show + ("normal",))
    rgb = shaded_rgb(w)
    rgb = _blend(rgb, L["urban"]["mask"], URBAN, .5)
    rgb = _blend(rgb, L["normal"]["mask"], WATER_NORMAL, .85)
    if "jur" in L: rgb = _blend(rgb, L["jur"]["mask"] & ~L["normal"]["mask"], WATER_JUR, .45)
    if "pir" in L: rgb = _blend(rgb, L["pir"]["mask"] & ~L["normal"]["mask"], WATER_PIR, .55)
    fig, ax = plt.subplots(figsize=figsize)
    ext = (w["x"].min() / 1000, w["x"].max() / 1000, w["y"].min() / 1000, w["y"].max() / 1000)
    ax.imshow(rgb, extent=ext, origin="upper", interpolation="bilinear")
    X, Y = w["x"] / 1000, w["y"] / 1000
    cs = ax.contour(X, Y, w["z"], levels=np.arange(np.floor(np.nanmin(w["z"]) / 20) * 20, np.nanmax(w["z"]), 20), colors="k", linewidths=.25, alpha=.35)
    ax.clabel(cs, levels=cs.levels[::2], fontsize=6, fmt="%d m")
    e = extremes(w)
    ax.scatter([e["alto"][0] / 1000], [e["alto"][1] / 1000], marker="^", s=140, c="white", ec="k", zorder=5)
    ax.annotate(f"ponto MAIS ALTO\n{e['alto'][2]:.0f} m", (e["alto"][0] / 1000, e["alto"][1] / 1000), xytext=(8, 8), textcoords="offset points",
                fontsize=9, weight="bold", bbox=dict(fc="white", ec="k", alpha=.85))
    ax.scatter([e["baixo"][0] / 1000], [e["baixo"][1] / 1000], marker="v", s=140, c="#ffeb3b", ec="k", zorder=5)
    ax.annotate(f"ponto MAIS BAIXO\n{e['baixo'][2]:.0f} m", (e["baixo"][0] / 1000, e["baixo"][1] / 1000), xytext=(8, -26), textcoords="offset points",
                fontsize=9, weight="bold", bbox=dict(fc="#ffeb3b", ec="k", alpha=.9))
    dp = D.dam_points().set_index("dam")
    for d in dp.index:
        x, y = dp.loc[d, "x_utm"] / 1000, dp.loc[d, "y_utm"] / 1000
        if ext[0] <= x <= ext[1] and ext[2] <= y <= ext[3]:
            ax.scatter([x], [y], marker="s", s=90, c=D.COLORS[d], ec="k", zorder=6); right = x > ext[0] + .75 * (ext[1] - ext[0])
            ax.annotate(D.DAMS[d].name.replace("UHE ", "Barragem "), (x, y), xytext=(-6 if right else 6, 6), textcoords="offset points", ha="right" if right else "left",
                        fontsize=8, weight="bold", color="white", bbox=dict(fc="#222", alpha=.7, ec="none"))
    handles = [plt.Line2D([], [], marker="s", ls="", color=WATER_NORMAL, label="Água em condição normal (OSM)"),
               plt.Line2D([], [], marker="s", ls="", color=URBAN, label="Áreas urbanizadas (IBGE 2019)")]
    if "jur" in L: handles.append(plt.Line2D([], [], marker="s", ls="", color=WATER_JUR, label="Mancha OFICIAL de Jurumirim (PAE p. 38)"))
    if "pir" in L: handles.append(plt.Line2D([], [], marker="s", ls="", color=WATER_PIR, label="Piraju: ESTIMATIVA EXPLORATÓRIA (ruptura TR 10.000)"))
    ax.legend(handles=handles, loc="lower right", fontsize=8, framealpha=.92)
    ax.set_title(REGIONS[key]["label"] + f" — relevo sombreado (exagero vertical {EXAG:.0f}×)", fontsize=11)
    ax.set_xlabel("E UTM 22S (km)"); ax.set_ylabel("N UTM 22S (km)")
    sm = plt.cm.ScalarMappable(cmap=HYPSO, norm=plt.Normalize(np.nanpercentile(w["z"], 1), np.nanpercentile(w["z"], 99)))
    cb = fig.colorbar(sm, ax=ax, shrink=.7); cb.set_label("Altitude (m): verde = baixo · marrom/branco = alto")
    fig.text(.01, .005, "Relevo: Copernicus GLO-30 (MDS 30 m, inclui vegetação). Água de Piraju: estimativa exploratória; não é o mapa do PAE.\n" + DISCLAIMER, fontsize=6.5, color="#444")
    fig.tight_layout(rect=(0, .03, 1, 1))
    return fig


# ---------------------------------------------------------------- 3D (matplotlib) e animações
def _surface_rgb(w, L, t: float | None, show):
    rgb = shaded_rgb(w)
    rgb = _blend(rgb, L["urban"]["mask"], URBAN, .55)
    rgb = _blend(rgb, L["normal"]["mask"], WATER_NORMAL, .9)
    for k, col in (("jur", WATER_JUR), ("pir", WATER_PIR)):
        if k in L and k in show:
            m = L[k]["mask"] & ~L["normal"]["mask"]
            if t is not None:
                m = m & (L[k]["t_arr"] <= t)
            rgb = _blend(rgb, m, col, .8)
    return rgb


def frame_3d(key: str, t: float | None, azim: float, elev: float = 38, show=("pir",), figsize=(12, 7), banner: str = "", w=None, L=None, step=None, zoom: float | None = None):
    w = w or window(key); L = L or layers(w, show + ("normal",)); step = step or REGIONS[key]["step"]
    rgb = _surface_rgb(w, L, t, show)[::step, ::step]
    z = np.where(np.isfinite(w["z"]), w["z"], np.nanmin(w["z"]))[::step, ::step]
    X, Y = w["x"][::step, ::step] / 1000, w["y"][::step, ::step] / 1000
    fig = plt.figure(figsize=figsize); ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, z, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    dx, dy = np.ptp(X), np.ptp(Y)
    ax.set_box_aspect((dx, dy, (np.ptp(z) / 1000) * EXAG), zoom=zoom or REGIONS[key].get('zoom', 1.55)); ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.text(.01, .965, banner or REGIONS[key]["label"], fontsize=11, weight="bold", va="top")
    fig.text(.99, .93, "laranja = área urbanizada (IBGE 2019) · azul = água normal · roxo = Piraju (estimativa) · vermelho = Jurumirim (oficial)", fontsize=7.5, ha="right", va="top")
    fig.text(.01, .01, f"Exagero vertical {EXAG:.0f}× · relevo Copernicus 30 m (MDS) · Piraju: ESTIMATIVA EXPLORATÓRIA, não é o mapa do PAE · "
             "avanço no tempo = INTERPOLAÇÃO ILUSTRATIVA\n" + DISCLAIMER, fontsize=6.5, color="#444")
    fig.subplots_adjust(left=0, right=1, top=.93, bottom=.06)
    return fig


def export_video(frames, out: Path, fps: int = 12, dpi: int = 100) -> Path:
    """`frames`: iterável de Figures. Codifica com ffmpeg (exige ffmpeg instalado)."""
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for i, f in enumerate(frames):
            f.savefig(Path(td) / f"f_{i:04d}.png", dpi=dpi); plt.close(f)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(Path(td) / "f_%04d.png"),
                        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def orbit_frames(key="piraju", n=72, show=("pir",)):
    w = window(key); L = layers(w, show + ("normal",))
    for i in range(n):
        az = -120 + 300 * i / n
        yield frame_3d(key, None, az, elev=34 + 6 * np.sin(2 * np.pi * i / n), show=show, w=w, L=L,
                       banner=f"Voo de reconhecimento: {REGIONS[key]['label']}")


def front_frames(key="piraju", show=("pir",), n=80, who="PIR"):
    """Água avançando: célula fica colorida quando t ≥ tempo de chegada interpolado entre seções tabeladas. Câmera orbita devagar."""
    w = window(key); L = layers(w, show + ("normal",))
    tmax = float(np.nanmax(np.concatenate([L[k]["t_arr"][np.isfinite(L[k]["t_arr"])] for k in show]))) * 1.02
    nome = {"pir": "Piraju (estimativa, ruptura TR 10.000)", "jur": "Jurumirim (mancha oficial do PAE)"}
    for i in range(n):
        t = tmax * i / (n - 1)
        yield frame_3d(key, t, azim=-100 + 70 * i / n, elev=36, show=show, w=w, L=L,
                       banner=f"{' + '.join(nome[k] for k in show)}: t = {int(t)//60} h {int(t)%60:02d} min após a ruptura")


# ---------------------------------------------------------------- 3D interativo (plotly): gire, aproxime, passe o mouse
def plotly_figure(key: str, show=("pir",), max_cells: int = 230):
    import plotly.graph_objects as go
    w = window(key); L = layers(w, show + ("normal",))
    st_ = max(1, int(np.ceil(max(w["z"].shape) / max_cells)))
    z = np.where(np.isfinite(w["z"]), w["z"], np.nanmin(w["z"]))[::st_, ::st_]
    X, Y = (w["x"][::st_, ::st_] - w["x"].min()) / 1000, (w["y"][::st_, ::st_] - w["y"].min()) / 1000
    colorscale = [[i / 7, c] for i, c in enumerate(["#1b5e3b", "#4c9a4f", "#bcd479", "#f2e394", "#d9a65f", "#a9743f", "#8a6a55", "#f5f0ea"])]
    fig = go.Figure(go.Surface(x=X, y=Y, z=z, colorscale=colorscale, colorbar=dict(title="Altitude (m)", len=.6), name="Terreno",
                               lighting=dict(ambient=.45, diffuse=.9, specular=.05, roughness=.9), lightposition=dict(x=-1500, y=2500, z=3000),
                               hovertemplate="Altitude %{z:.0f} m<extra>terreno</extra>"))

    def overlay(mask, zz, color, name, opacity):
        m = mask[::st_, ::st_]
        if m.any():
            fig.add_trace(go.Surface(x=X, y=Y, z=np.where(m, zz[::st_, ::st_], np.nan), colorscale=[[0, color], [1, color]], showscale=False, opacity=opacity,
                                     name=name, hovertemplate=name + "<extra></extra>", lighting=dict(ambient=.9)))
    zfill = np.where(np.isfinite(w["z"]), w["z"], 0)
    overlay(L["urban"]["mask"], zfill + 1.5, "#ff7a00", "Área urbanizada (IBGE 2019)", .75)
    overlay(L["normal"]["mask"], zfill + 0.8, WATER_NORMAL, "Água em condição normal (OSM)", .95)
    if "jur" in L:
        overlay(L["jur"]["mask"] & ~L["normal"]["mask"], zfill + 2.0, WATER_JUR, "Mancha OFICIAL de Jurumirim (PAE p. 38)", .7)
    if "pir" in L:
        overlay(L["pir"]["mask"] & ~L["normal"]["mask"], np.where(np.isfinite(L["pir"]["z_water"]), L["pir"]["z_water"], 0), WATER_PIR,
                "Piraju: ESTIMATIVA EXPLORATÓRIA (superfície da água na cota do PAE)", .7)
    dx, dy, dz = np.ptp(X), np.ptp(Y), np.ptp(z) / 1000 * EXAG
    fig.update_layout(height=640, margin=dict(l=0, r=0, t=30, b=0), title=f"{REGIONS[key]['label']} (exagero vertical {EXAG:.0f}×)",
                      scene=dict(aspectmode="manual", aspectratio=dict(x=dx / max(dx, dy), y=dy / max(dx, dy), z=dz / max(dx, dy)),
                                 xaxis=dict(title="km", showbackground=False), yaxis=dict(title="km", showbackground=False),
                                 zaxis=dict(title="Altitude (m)", showbackground=False), camera=dict(eye=dict(x=-.9, y=-1.5, z=1.0))))
    return fig


def png_bytes(fig, dpi=110) -> bytes:
    import io
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight"); plt.close(fig)
    return buf.getvalue()
