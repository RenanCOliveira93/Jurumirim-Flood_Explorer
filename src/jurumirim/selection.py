"""Filtro do dashboard ('Por Barragem Isolada' × 'Todas barragens selecionadas') e estado da onda no tempo.

Regra central: 'Todas' = SOBREPOSIÇÃO de cenários isolados independentes. Cada cenário tem o relógio da própria
ruptura (t = 0 na brecha daquela barragem). Nenhuma onda rompe a barragem seguinte: ruptura em cascata é
`not_modelled` e nenhum tempo, mancha ou probabilidade de cascata é produzido aqui.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import dams as D

MODE_ISOLADA = "Por Barragem Isolada"
MODE_TODAS = "Todas barragens selecionadas"
MODES = (MODE_ISOLADA, MODE_TODAS)
NOT_CASCADE = ("Sobreposição de cenários isolados e independentes: cada barragem usa o relógio da própria ruptura "
               "(t = 0 na sua brecha). Nenhuma onda rompe a barragem seguinte; ruptura em cascata NÃO foi modelada.")
INTERP_BANNER = "INTERPOLAÇÃO ILUSTRATIVA, não resultado hidráulico oficial"


@dataclass(frozen=True)
class Selection:
    mode: str
    rows: tuple[tuple[str, str | None], ...]  # (dam_id, scenario)

    @property
    def dam_ids(self) -> list[str]:
        return [d for d, _ in self.rows]

    @property
    def is_all(self) -> bool:
        return self.mode == MODE_TODAS

    def scenario(self, dam_id: str) -> str | None:
        return dict(self.rows).get(dam_id)

    def with_sections(self) -> list[tuple[str, str | None]]:
        return [(d, s) for d, s in self.rows if D.DAMS[d].has_sections]

    def without_sections(self) -> list[str]:
        return [d for d, _ in self.rows if not D.DAMS[d].has_sections]


def make(mode: str, chosen: list[str], scenarios: dict[str, str | None] | None = None) -> Selection:
    if mode not in MODES:
        raise ValueError(f"modo inválido: {mode!r}")
    if not chosen:
        raise ValueError("selecione ao menos uma barragem")
    unknown = [c for c in chosen if c not in D.DAMS]
    if unknown:
        raise ValueError(f"barragem desconhecida: {unknown}")
    return Selection(mode, tuple(D.selection_rows("isolada" if mode == MODE_ISOLADA else "todas", chosen, scenarios or {})))


def sections_for(sel: Selection) -> pd.DataFrame:
    """Seções de todas as barragens selecionadas que as têm, no esquema comum + colunas dam/scenario/label."""
    parts = []
    for dam, sc in sel.with_sections():
        df = D.sections(dam, sc).copy()
        df.insert(0, "dam", dam)
        df.insert(1, "scenario", sc or "")
        df.insert(2, "label", D.sel_label(dam, sc))
        parts.append(df)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["dam", "scenario", "label", *D.COMMON])


def t_max(sel: Selection) -> int:
    """Último instante com dado documentado em qualquer cenário selecionado (min)."""
    s = sections_for(sel)
    if s.empty:
        return 0
    return int(np.nanmax(s[["t_frente_min", "t_pico_min"]].to_numpy(dtype=float)))


def state_at(sel: Selection, t_min: float) -> pd.DataFrame:
    """Estado de cada seção em t (minutos desde a ruptura DA PRÓPRIA barragem).

    estado: 'atingida' (t_frente ≤ t), 'não atingida' (t_frente > t) ou 'sem tempo no PAE' (valor ausente).
    """
    s = sections_for(sel)
    if s.empty:
        return s.assign(estado=[], pico_passou=[])
    tf = s.t_frente_min
    s["estado"] = np.where(tf.isna(), "sem tempo no PAE", np.where(tf <= t_min, "atingida", "não atingida"))
    s["pico_passou"] = np.where(s.t_pico_min.isna(), None, s.t_pico_min <= t_min)
    return s


def summary_at(sel: Selection, t_min: float) -> pd.DataFrame:
    """Resumo por barragem em t: seções atingidas, trecho alcançado e vazão de pico na última seção atingida."""
    st = state_at(sel, t_min)
    rows = []
    for dam, sc in sel.rows:
        d = D.DAMS[dam]
        if not d.has_sections:
            rows.append(dict(barragem=d.name, cenario="—", secoes_atingidas="sem tabela de seções no PAE", ate_km=None,
                             ultima_secao="—", vazao_pico_ultima_m3s=None))
            continue
        g = st[st.dam == dam]
        hit = g[g.estado == "atingida"]
        last = hit.sort_values("distancia_km").iloc[-1] if len(hit) else None
        rows.append(dict(barragem=d.name, cenario=D.sel_label(dam, sc).split(" — ")[-1],
                         secoes_atingidas=f"{len(hit)} de {len(g)}",
                         ate_km=None if last is None else float(last.distancia_km),
                         ultima_secao="—" if last is None else last.secao,
                         vazao_pico_ultima_m3s=None if last is None or pd.isna(last.vazao_pico_m3s) else float(last.vazao_pico_m3s)))
    return pd.DataFrame(rows)


def front_km(df: pd.DataFrame, t_min: float) -> float | None:
    """Posição da frente (km) por interpolação LINEAR entre seções com tempo documentado. ILUSTRAÇÃO.

    None fora do intervalo tabelado (antes da primeira seção ou depois da última com tempo): não se extrapola.
    """
    g = df.dropna(subset=["t_frente_min"]).sort_values("distancia_km")
    t, x = g.t_frente_min.to_numpy(float), g.distancia_km.to_numpy(float)
    if len(g) < 2 or t_min < t.min() or t_min > t.max():
        return None
    order = np.argsort(t, kind="stable")
    return float(np.interp(t_min, t[order], x[order]))


def coverage_notes(sel: Selection) -> list[str]:
    """O que NÃO existe para cada barragem selecionada (mostrado ao usuário; nada é preenchido por suposição)."""
    notes = []
    for dam, _ in sel.rows:
        d = D.DAMS[dam]
        if not d.has_polygon:
            notes.append(f"{d.name}: mancha georreferenciada indisponível. {d.note}".strip())
        elif d.note:
            notes.append(f"{d.name}: {d.note}")
    return notes
