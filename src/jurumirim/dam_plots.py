"""Gráficos plotly por barragem/seleção (páginas Seções, Comparação e Simulação)."""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import dams as D
from . import selection as S

PANELS = [("t_frente_min", "Chegada da onda (min)", False), ("t_pico_min", "Tempo até a vazão máxima (min)", False),
          ("vel_max_ms", "Velocidade máxima (m/s)", False), ("vazao_pico_m3s", "Vazão de pico (m³/s)", True)]


def _name(dam, sc):
    return D.sel_label(dam, sc).replace("UHE ", "")


def section_panels(df, panels=PANELS) -> go.Figure:
    """df no esquema comum + dam/scenario. Um traço por (barragem, cenário); eixo x = distância ao eixo da barragem."""
    cols = 2
    rows = -(-len(panels) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[p[1] for p in panels])
    for (dam, sc), g in df.groupby(["dam", "scenario"], sort=False):
        for i, (col, _, log) in enumerate(panels):
            if g[col].notna().any():
                fig.add_trace(go.Scatter(x=g.distancia_km, y=g[col], mode="lines+markers", name=_name(dam, sc),
                                         legendgroup=dam, showlegend=(i == 0), text=g.secao, line=dict(color=D.COLORS[dam]),
                                         hovertemplate="%{text}<br>%{x} km<br>%{y}<extra>" + _name(dam, sc) + "</extra>"),
                              row=i // cols + 1, col=i % cols + 1)
            fig.update_xaxes(title_text="Distância ao eixo da barragem (km)", row=i // cols + 1, col=i % cols + 1)
            if log:
                fig.update_yaxes(type="log", row=i // cols + 1, col=i % cols + 1)
    fig.update_layout(height=320 * rows + 60, legend=dict(orientation="h", y=-0.12))
    return fig


def time_distance(df, t_min: float | None = None, interpolate: bool = False) -> go.Figure:
    """Distância × tempo (relógio PRÓPRIO de cada barragem). Linha vertical = t atual; estrela = frente interpolada."""
    fig = go.Figure()
    for (dam, sc), g in df.groupby(["dam", "scenario"], sort=False):
        g = g.dropna(subset=["t_frente_min"]).sort_values("distancia_km")
        off = float(g.offset_min.iloc[0]) if "offset_min" in g and len(g) and g.offset_min.iloc[0] == g.offset_min.iloc[0] else 0.0
        chained = "offset_min" in g and bool(g.offset_min.fillna(0).ne(0).any())
        g = g.assign(t_plot=g.t_frente_min + off)
        fig.add_trace(go.Scatter(x=g.t_plot, y=g.distancia_km, mode="lines+markers", name=_name(dam, sc), text=g.secao,
                                 line=dict(color=D.COLORS[dam], dash="dot" if interpolate else "solid"),
                                 hovertemplate="%{text}<br>%{x} min<br>%{y} km<extra>" + _name(dam, sc) + "</extra>"))
        if t_min is not None and interpolate:
            km = S.front_km(g, t_min - off)
            if km is not None:
                fig.add_trace(go.Scatter(x=[t_min], y=[km], mode="markers", marker=dict(symbol="star", size=16, color="#ff9800",
                                                                                         line=dict(width=1, color="#000")),
                                         name=f"frente interpolada ({dam})", showlegend=False,
                                         hovertemplate=f"{INTERP}<br>{km:.2f} km<extra></extra>"))
    if t_min is not None:
        fig.add_vline(x=t_min, line=dict(color="#555", dash="dash"))
    fig.update_layout(height=420, xaxis_title=("Tempo desde a ruptura da 1ª barragem (min) — HIPÓTESE de encadeamento" if (df.get("offset_min") is not None and df.offset_min.fillna(0).ne(0).any())
                                  else "Tempo desde a ruptura DA PRÓPRIA barragem (min)"),
                      yaxis_title="Distância ao longo do rio (km)", legend=dict(orientation="h", y=-0.2))
    return fig


INTERP = S.INTERP_BANNER
