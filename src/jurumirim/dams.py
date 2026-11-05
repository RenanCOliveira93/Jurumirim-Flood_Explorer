"""Registro de barragens e camada unificada de seções. Incremental: cada barragem tem seus próprios arquivos
(data/processed/dams/<ID>/); o conjunto de Jurumirim (fase 1-2) continua onde estava e é só *lido* aqui."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache

import pandas as pd

from . import data, paths

DAMS_DIR = paths.PROCESSED / "dams"
COMMON = ["secao", "descricao", "distancia_km", "t_frente_min", "t_pico_min", "vazao_pico_m3s", "vel_max_ms",
          "prof_max_m", "elev_max_m", "sobrelevacao_m", "x_utm", "y_utm", "posicao"]


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    note: str = ""


@dataclass(frozen=True)
class Dam:
    id: str
    name: str
    owner: str
    order: int  # posição na cascata (1 = montante)
    document: str
    scenarios: tuple[Scenario, ...] = field(default_factory=tuple)
    has_polygon: bool = False
    has_sections: bool = True
    note: str = ""


DAMS: dict[str, Dam] = {
    "JUR": Dam("JUR", "UHE Jurumirim", "CTG Brasil", 1, "PAE Externo UHE Jurumirim (jan/2026)",
               (Scenario("ruptura_568", "Ruptura isolada em dia seco, N.A. 568,00 m",
                         "Cenário adotado no PAE; modelagem termina na barragem de Piraju."),),
               has_polygon=True),
    "PIR": Dam("PIR", "UHE Piraju", "CBA (Cia. Brasileira de Alumínio)", 2, "PAE UHE Piraju (emissão 20/10/2025)",
               (Scenario("ruptura_tr10000", "Ruptura isolada, TR 10.000 anos (N.A. inicial 532,70 m)",
                         "Mais conservador; brecha de 179,50 × 20,50 m em 6 min."),
                Scenario("ruptura_tr10", "Ruptura isolada, TR 10 anos (N.A. inicial 531,50 m)")),
               note="Mancha georreferenciada indisponível: mapas no Apêndice 9 não constam do PDF."),
    "PAR": Dam("PAR", "UHE Paranapanema", "Enel Green Power", 3, "PAE UHE Paranapanema (rev. 08, 15/12/2025)",
               (), has_sections=False,
               note="O PDF não traz tabela de seções nem tempos de chegada (estão nos mapas do Anexo 2, não incluídos)."),
}


def sel_label(dam_id: str, scenario: str | None) -> str:
    d = DAMS[dam_id]
    sc = next((s for s in d.scenarios if s.id == scenario), None)
    return f"{d.name} — {sc.label}" if sc else d.name


def default_scenario(dam_id: str) -> str | None:
    s = DAMS[dam_id].scenarios
    return s[0].id if s else None


@lru_cache(maxsize=1)
def facts() -> pd.DataFrame:
    """Fatos por barragem. psb_* (PSB com 'Sigilo: Interno') só existe se gerado localmente."""
    parts = [pd.read_csv(f) for f in sorted(DAMS_DIR.glob("*/facts.csv")) + sorted(DAMS_DIR.glob("*/psb_facts.csv"))]
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    out["value_num"] = pd.to_numeric(out["value"], errors="coerce")  # 'value' mistura números e texto
    return out


def has_sections(dam_id: str, scenario: str | None = None) -> bool:
    return DAMS[dam_id].has_sections and (scenario is not None or dam_id == "JUR")


@lru_cache(maxsize=16)
def sections(dam_id: str, scenario: str | None = None) -> pd.DataFrame:
    """Seções no esquema COMUM (colunas ausentes = NaN). Posição: 'documentada' (UTM do PAE) ou 'ilustrativa'."""
    if dam_id == "JUR":
        s = data.sections()
        out = pd.DataFrame(dict(secao=s.id, descricao=s.descricao, distancia_km=s.distancia_km,
                                t_frente_min=s.tempo_chegada_min, vazao_pico_m3s=s.vazao_pico_m3s,
                                vel_max_ms=s.velocidade_ms, sobrelevacao_m=s.sobrelevacao_m,
                                x_utm=s.x_utm, y_utm=s.y_utm, posicao="documentada (UTM do PAE)"))
    elif dam_id == "PIR":
        tr = {"ruptura_tr10000": 10000, "ruptura_tr10": 10}[scenario or default_scenario("PIR")]
        r = pd.read_csv(DAMS_DIR / "PIR" / "sections_rupture.csv")
        r = r[r.tr_anos == tr]
        pos = pd.read_csv(DAMS_DIR / "PIR" / "sections_positions.csv")
        out = r.merge(pos[["secao", "x_utm", "y_utm", "posicao"]], on="secao", how="left")
        out = out.rename(columns={"vazao_max_m3s": "vazao_pico_m3s", "vel_max_ms": "vel_max_ms"})
        out["descricao"] = ""
    else:
        raise KeyError(f"{dam_id} não tem tabela de seções no PDF")
    for c in COMMON:
        if c not in out.columns:
            out[c] = float("nan") if c != "posicao" else ""
    return out[COMMON].reset_index(drop=True)


def dam_points() -> pd.DataFrame:
    """Barragens com posição OFICIAL (coordenada citada no próprio PAE). Fonte e página junto."""
    return pd.read_csv(DAMS_DIR / "dams_positions.csv")


def natural_sections(tr: int = 10000) -> pd.DataFrame:
    """Piraju, cenário SEM ruptura (Tabela 9, PDF p.62)."""
    n = pd.read_csv(DAMS_DIR / "PIR" / "sections_natural.csv")
    return n[n.tr_anos == tr].reset_index(drop=True)


def validation() -> dict:
    f = DAMS_DIR / "validation.json"
    return json.loads(f.read_text()) if f.exists() else {}


def selection_rows(mode: str, chosen: list[str], scenarios: dict[str, str | None]) -> list[tuple[str, str | None]]:
    """Normaliza o filtro do dashboard. mode: 'isolada' (uma barragem) ou 'todas' (as selecionadas)."""
    if mode == "isolada":
        chosen = chosen[:1]
    return [(d, scenarios.get(d) or default_scenario(d)) for d in sorted(chosen, key=lambda d: DAMS[d].order)]


# Cenários HEC-RAS do PAE Paranapanema (seção 9, p.14). Valores como escritos no PAE; sem tempos nem seções.
PAR_SCENARIOS = pd.DataFrame([
    dict(cenario="TR 100 anos", vazao_m3s=1652.57, na_montante_m=504.77),
    dict(cenario="TR 10.000 anos", vazao_m3s=2800.00, na_montante_m=506.75),
    dict(cenario="Ruptura hipotética (hidrograma 'Dam Break')", vazao_m3s=2420.13, na_montante_m=505.71),
    dict(cenario="Abertura total dos vertedouros de comporta", vazao_m3s=1842.00, na_montante_m=506.75),
]).assign(source_document="PAE UHE Paranapanema (rev. 08)", source_page="14 (PDF = impressa)")

COLORS = {"JUR": "#1f77b4", "PIR": "#d62728", "PAR": "#2ca02c"}


def compare_piraju(tr: int) -> pd.DataFrame:
    """Piraju: ruptura (Tabela 10) × cheia natural sem ruptura (Tabela 9) na MESMA TR, por seção (TR 10 ou 10.000)."""
    sc = {10000: "ruptura_tr10000", 10: "ruptura_tr10"}[tr]
    r = sections("PIR", sc).set_index("secao")
    n = natural_sections(tr).set_index("secao")
    out = pd.DataFrame(dict(distancia_km=r.distancia_km, elev_max_ruptura_m=r.elev_max_m, elev_max_natural_m=n.elev_max_m,
                            prof_max_ruptura_m=r.prof_max_m, prof_max_natural_m=n.prof_max_m,
                            vel_max_ruptura_ms=r.vel_max_ms, vel_max_natural_ms=n.vel_max_ms))
    out["dif_cota_m"] = (out.elev_max_ruptura_m - out.elev_max_natural_m).round(2)
    return out.reset_index()


@lru_cache(maxsize=1)
def river_xy():
    """Eixo OSM do rio (UTM 22S) de Jurumirim até a última seção de Piraju: contexto visual (ILUSTRAÇÃO), não dado do PAE."""
    import numpy as np
    from shapely.geometry import Point

    from . import riverpos
    river = riverpos.river_line(paths.RAW / "osm_waterways.json")
    pts = dam_points().set_index("dam")
    s_a = river.project(Point(pts.loc["JUR", "x_utm"], pts.loc["JUR", "y_utm"]))
    s_b = river.project(Point(pts.loc["PIR", "x_utm"], pts.loc["PIR", "y_utm"])) + 32.35e3
    ss = np.linspace(min(s_a, s_b), min(max(s_a, s_b), river.length), 600)
    xy = np.array([river.interpolate(s).coords[0] for s in ss])
    return xy[:, 0], xy[:, 1]
