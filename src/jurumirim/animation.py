"""Timeline técnica: frente da onda nas seções DOCUMENTADAS do PAE (p. 38).

Modo padrão ("documentado"): cada seção acende no instante tabelado; nada é interpolado.
Modo opcional (interpolate=True): marcador ao longo da polilinha entre seções com tempo interpolado
linearmente — rotulado como INTERPOLAÇÃO ILUSTRATIVA, não resultado hidráulico oficial.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import DISCLAIMER, data
from . import dams as D
from . import selection as S
from .paths import OUTPUTS

BANNER_DOC = "DADO OFICIAL: tempos de chegada nas seções do PAE (p. 38) — sem interpolação"
BANNER_INT = "INTERPOLAÇÃO ILUSTRATIVA, não resultado hidráulico oficial"


def frame(t_min: float, interpolate=False, figsize=(10.8, 7.2)):
    p = data.polygons(); s = data.sections(); pts = data.section_points()
    fig, ax = plt.subplots(figsize=figsize)
    p[p.classe == "ENVOLTORIA_RUPTURA"].plot(ax=ax, color="#dddddd", ec="#888", lw=.5)
    data.urbanizadas().plot(ax=ax, color="#ff9800", alpha=.5)
    xs, ys = pts.geometry.x.values, pts.geometry.y.values
    ax.plot(xs, ys, "-", color="#bbb", lw=.8, zorder=2)
    reached = (s.tempo_chegada_min <= t_min).values
    ax.scatter(xs[~reached], ys[~reached], s=60, c="#ffffff", ec="k", zorder=4)
    ax.scatter(xs[reached], ys[reached], s=80, c="#d62728", ec="k", zorder=5)
    for i, r in s.iterrows():
        ax.annotate(f"{r.id[3:]}\n{r.tempo_chegada_hhmm}", (xs[i], ys[i]), fontsize=6, xytext=(5, 5), textcoords="offset points")
    if interpolate:
        tt = s.tempo_chegada_min.values.astype(float)
        if tt[0] <= t_min < tt[-1]:
            k = np.searchsorted(tt, t_min, side="right") - 1
            k = min(k, len(tt) - 2)
            f = 0 if tt[k + 1] == tt[k] else (t_min - tt[k]) / (tt[k + 1] - tt[k])
            ax.scatter([xs[k] + f * (xs[k + 1] - xs[k])], [ys[k] + f * (ys[k + 1] - ys[k])], marker="*", s=260, c="#ff9800",
                       ec="k", zorder=6)
    ax.set_xlim(660000, 684000); ax.set_ylim(7430000, 7441500); ax.set_aspect("equal")
    ax.set_xlabel("E UTM 22S (m)"); ax.set_ylabel("N UTM 22S (m)")
    ax.set_title(f"Frente da onda — t = {int(t_min)//60}h{int(t_min)%60:02d} após a ruptura hipotética", fontsize=12)
    ax.text(.01, .985, BANNER_INT if interpolate else BANNER_DOC, transform=ax.transAxes, va="top", fontsize=8,
            bbox=dict(fc="#fff3cd" if interpolate else "#e3f2fd", ec="#999"))
    fig.text(.01, .01, "Cenário: ruptura isolada em dia seco, N.A. 568,00 m. Não é previsão.\n" + DISCLAIMER, fontsize=6.5, color="#555")
    fig.subplots_adjust(bottom=.1)
    return fig


def export_frames(outdir: Path = OUTPUTS / "frames", times=None, interpolate=False):
    outdir.mkdir(parents=True, exist_ok=True)
    times = list(range(0, 126, 1)) if times is None else times
    paths = []
    for i, t in enumerate(times):
        fig = frame(t, interpolate)
        pth = outdir / f"frame_{i:04d}.png"
        fig.savefig(pth, dpi=100); plt.close(fig); paths.append(pth)
    return paths


def export_mp4(out: Path = OUTPUTS / "timeline_onda.mp4", interpolate=False, fps=12):
    frames_dir = out.parent / "frames"
    for old in frames_dir.glob("frame_*.png"):
        old.unlink()
    export_frames(frames_dir, interpolate=interpolate)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames_dir / "frame_%04d.png"),
           "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)]
    subprocess.run(cmd, check=True)
    return out


# ---------------------------------------------------------------- quadros por SELEÇÃO de barragens (filtro do dashboard)
def frame_selection(sel: S.Selection, t_min: float, interpolate=False, figsize=(14, 7)):
    """Mapa (esq.) + distância×tempo (dir.). Cada barragem usa o relógio da PRÓPRIA ruptura; nunca é cascata."""
    st_ = S.state_at(sel, t_min)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=figsize, gridspec_kw=dict(width_ratios=[1.1, 1]))
    rx, ry = D.river_xy()
    ax.plot(rx, ry, color="#9ecae1", lw=1.5, zorder=1)
    if "JUR" in sel.dam_ids:
        p = data.polygons()
        p[p.classe == "ENVOLTORIA_RUPTURA"].plot(ax=ax, color="#dddddd", ec="#888", lw=.5, zorder=0)
    xs_all, ys_all = [], []
    for dam, sc in sel.rows:
        col = D.COLORS[dam]
        g = st_[st_.dam == dam]
        for estado, face, edge in (("atingida", col, "k"), ("não atingida", "white", col), ("sem tempo no PAE", "#bbbbbb", "#555"), ("ainda não rompeu (hipótese)", "#eeeeee", "#999")):
            q = g[g.estado == estado]
            ax.scatter(q.x_utm, q.y_utm, s=70 if estado == "atingida" else 45, c=face, ec=edge, zorder=4, label=None)
        xs_all += list(g.x_utm); ys_all += list(g.y_utm)
    dp = D.dam_points().set_index("dam")
    for dam in sel.dam_ids:
        ax.scatter([dp.loc[dam, "x_utm"]], [dp.loc[dam, "y_utm"]], marker="s", s=110, c=D.COLORS[dam], ec="k", zorder=6)
        ax.annotate(D.DAMS[dam].name.replace("UHE ", ""), (dp.loc[dam, "x_utm"], dp.loc[dam, "y_utm"]), fontsize=8,
                    xytext=(6, 6), textcoords="offset points", weight="bold")
        xs_all.append(dp.loc[dam, "x_utm"]); ys_all.append(dp.loc[dam, "y_utm"])
    if interpolate:
        for dam, sc in sel.with_sections():
            km = S.front_km(D.sections(dam, sc), t_min - (S.offsets(sel).get(dam) or 0))
            if km is not None:
                g = D.sections(dam, sc).dropna(subset=["x_utm"]).sort_values("distancia_km")
                ax.scatter([np.interp(km, g.distancia_km, g.x_utm)], [np.interp(km, g.distancia_km, g.y_utm)], marker="*", s=300,
                           c="#ff9800", ec="k", zorder=7)
    pad = 2500
    ax.set_xlim(min(xs_all) - pad, max(xs_all) + pad); ax.set_ylim(min(ys_all) - pad, max(ys_all) + pad); ax.set_aspect("equal")
    ax.set_xlabel("E UTM 22S (m)"); ax.set_ylabel("N UTM 22S (m)")
    ax.set_title("Seções atingidas (cheio) × não atingidas (vazio); cinza = sem tempo no PAE", fontsize=9)
    for dam, sc in sel.with_sections():
        g = st_[st_.dam == dam].dropna(subset=["t_frente_min"]).sort_values("distancia_km")
        ax2.plot(g.t_frente_min + g.offset_min.fillna(0), g.distancia_km, "o-", color=D.COLORS[dam], ms=4, label=D.sel_label(dam, sc).replace("UHE ", ""))
    ax2.axvline(t_min, color="#555", ls="--")
    ax2.set_xlabel("Tempo desde a ruptura da 1ª barragem (min), HIPÓTESE" if sel.chain else "Tempo desde a ruptura DA PRÓPRIA barragem (min)"); ax2.set_ylabel("Distância ao longo do rio (km)")
    ax2.grid(alpha=.3); ax2.legend(fontsize=7, loc="upper left")
    fig.suptitle(f"t = {int(t_min)//60}h{int(t_min)%60:02d} " + ("após a ruptura de Jurumirim (encadeamento HIPOTÉTICO)" if sel.chain else "após a ruptura hipotética de cada barragem (relógios independentes)"),
                 fontsize=12, y=.985)
    banner = (S.INTERP_BANNER + " (estrela)" if interpolate else "DADO OFICIAL: tempos tabelados nas seções dos PAEs; sem interpolação")
    if sel.is_all:
        banner += "\n" + textwrap.fill(S.CHAIN_BANNER if sel.chain else S.NOT_CASCADE, 165)
    fig.text(.01, .94, banner, fontsize=7, va="top", bbox=dict(fc="#fff3cd" if interpolate else "#e3f2fd", ec="#999"))
    fig.text(.01, .01, "Posições de Piraju: ILUSTRAÇÃO (km sobre eixo OSM). Sem mancha de Piraju/Paranapanema (não consta dos PDFs). "
             "Não é previsão.\n" + DISCLAIMER, fontsize=6.5, color="#555")
    fig.subplots_adjust(top=.80, bottom=.12, wspace=.22)
    return fig


def export_selection_mp4(sel: S.Selection, out: Path = OUTPUTS / "timeline_selecao.mp4", step=3, fps=8, interpolate=False):
    """Exporta MP4 da seleção (frames temporários em outputs/frames_selecao, removidos ao final)."""
    import shutil
    d = out.parent / "frames_selecao"
    shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    for i, t in enumerate(range(0, S.t_max(sel) + step, step)):
        fig = frame_selection(sel, t, interpolate)
        fig.savefig(d / f"frame_{i:04d}.png", dpi=90); plt.close(fig)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(d / "frame_%04d.png"),
           "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(d, ignore_errors=True)
    return out
