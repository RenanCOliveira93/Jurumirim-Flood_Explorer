"""Perguntas sobre extensão lateral, área urbana, altitude e 'força' da água, respondidas só com dados dos PAEs e do relevo.

Rótulos: tudo aqui é DERIVADO DO PAE (valores tabelados) ou ESTIMATIVA EXPLORATÓRIA (depende da mancha estimada de Piraju).
Não há classificação de segurança de imóveis/endereços/rotas, probabilidade de ruptura nem simulação hidráulica.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import substring, unary_union

from . import dams as D
from . import paths

OUT = paths.PROCESSED / "dams" / "exposure"
RHO, G = 1000.0, 9.81  # kg/m³, m/s²


def load(name: str) -> pd.DataFrame:
    f = OUT / f"{name}.csv"
    return pd.read_csv(f) if f.exists() else pd.DataFrame()


# ---------------------------------------------------------------- força (a partir de velocidade e profundidade tabeladas)
def force_table() -> pd.DataFrame:
    """Por seção: velocidade e profundidade (PAE) → pressão dinâmica ½ρv², carga de velocidade v²/2g e índice h·v.
    São valores MÁXIMOS NA SEÇÃO DO CANAL (HEC-RAS); não são valores no terreno junto a imóveis."""
    rows = []
    jur = D.sections("JUR")
    for _, r in jur.iterrows():
        rows.append(dict(barragem="Jurumirim", cenario="ruptura (568,00 m)", secao=r.secao, km=r.distancia_km, vel_ms=r.vel_max_ms,
                         prof_m=np.nan, vazao_m3s=r.vazao_pico_m3s, origem="PAE Jurumirim p. 38"))
    for tr in (10000, 10):
        rup = D.sections("PIR", {10000: "ruptura_tr10000", 10: "ruptura_tr10"}[tr])
        nat = D.natural_sections(tr)
        for _, r in rup[rup.secao != "ST-00"].iterrows():
            rows.append(dict(barragem="Piraju", cenario=f"ruptura TR {tr}", secao=r.secao, km=r.distancia_km, vel_ms=r.vel_max_ms,
                             prof_m=r.prof_max_m, vazao_m3s=r.vazao_pico_m3s, origem="PAE Piraju Tabela 10 (OCR)"))
        for _, r in nat[nat.secao != "ST-00"].iterrows():
            rows.append(dict(barragem="Piraju", cenario=f"cheia natural TR {tr}", secao=r.secao, km=r.distancia_km, vel_ms=r.vel_max_ms,
                             prof_m=r.prof_max_m, vazao_m3s=r.get("vazao_max_m3s", np.nan), origem="PAE Piraju Tabela 9 (OCR)"))
    f = pd.DataFrame(rows)
    f["pressao_dinamica_kpa"] = 0.5 * RHO * f.vel_ms ** 2 / 1000
    f["carga_velocidade_m"] = f.vel_ms ** 2 / (2 * G)
    f["h_x_v_m2s"] = f.prof_m * f.vel_ms
    return f


# ---------------------------------------------------------------- extensão lateral
def _extent(geom, near: float) -> float:
    """Distância (m) da origem do transecto até a borda mais distante do trecho de `geom` que contém/toca a origem (a ≤ near m)."""
    if geom.is_empty:
        return 0.0
    parts = list(getattr(geom, "geoms", [geom]))
    best, ok = 0.0, False
    for p in parts:
        if p.geom_type not in ("LineString", "MultiLineString"):
            continue
        for ls in getattr(p, "geoms", [p]):
            c = np.array(ls.coords)
            d0 = np.hypot(*(c[0] - ORIG))
            d1 = np.hypot(*(c[-1] - ORIG))
            lo, hi = min(d0, d1), max(d0, d1)
            if lo <= near:
                best, ok = max(best, hi), True
    return best if ok else 0.0


ORIG = np.zeros(2)


def lateral(poly, water, line: LineString, step_m: float = 500.0, half_m: float = 6000.0, near_m: float = 250.0) -> pd.DataFrame:
    """Em transectos perpendiculares ao eixo: borda da mancha − borda da água normal, por margem. ILUSTRAÇÃO (eixo OSM)."""
    global ORIG
    rows = []
    L = line.length
    for s in np.arange(0, L, step_m):
        p = line.interpolate(s)
        a, b = line.interpolate(max(s - 20, 0)), line.interpolate(min(s + 20, L))
        t = np.array([b.x - a.x, b.y - a.y]); t = t / np.hypot(*t); n = np.array([-t[1], t[0]])
        ORIG = np.array([p.x, p.y])
        for side, sg in (("esquerda", 1), ("direita", -1)):
            seg = LineString([(p.x, p.y), (p.x + sg * n[0] * half_m, p.y + sg * n[1] * half_m)])
            fe, ne = _extent(poly.intersection(seg), near_m), _extent(water.intersection(seg), near_m)
            rows.append(dict(km=round(s / 1000, 2), margem=side, mancha_m=round(fe), agua_normal_m=round(ne),
                             avanco_alem_da_margem_m=round(max(0.0, fe - ne))))
    return pd.DataFrame(rows)


def lateral_summary(tr: pd.DataFrame) -> pd.DataFrame:
    """Resumo por cenário: transectos onde a mancha toca o eixo (mancha_m > 0)."""
    g = tr[tr.mancha_m > 0]
    out = g.groupby("cenario").avanco_alem_da_margem_m.agg(transectos="count", mediana_m="median",
                                                         p90_m=lambda x: x.quantile(.9), maximo_m="max").round(0).reset_index()
    out["largura_total_mediana_m"] = g.groupby(["cenario", "km"]).mancha_m.sum().groupby("cenario").median().round(0).values
    return out


# ---------------------------------------------------------------- área urbana e altitude
def urban_exposure(polys: dict[str, "shapely.geometry.base.BaseGeometry"], lines: dict[str, LineString],
                   profiles: dict[str, tuple]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(1) % da área urbanizada IBGE 2019 de Piraju tocada por cenário; (2) altitude de cada mancha urbana próxima do rio."""
    import rasterio.features
    from . import bathtub as B, gis
    urb, mun = gis.load_urbanizadas(), gis.load_municipios()
    pir = mun[mun.nome == "Piraju"].geometry.iloc[0]
    urb = urb[urb.geometry.representative_point().within(pir)].copy()
    urb["area_km2"] = urb.geometry.area / 1e6
    total = float(urb.area_km2.sum())
    share = []
    for k, poly in polys.items():
        hit = urb.geometry.intersection(poly).area.sum() / 1e6
        share.append(dict(cenario=k, area_urbanizada_piraju_km2=round(total, 3), area_tocada_km2=round(float(hit), 4),
                          pct_da_area_urbanizada=round(100 * hit / total, 2),
                          poligonos_tocados=int((urb.geometry.intersection(poly).area > 0).sum()), poligonos_total=len(urb)))
    dem, tr = B._dem_utm()
    rows = []
    river = unary_union(list(lines.values()))
    for i, u in urb.iterrows():
        d = float(u.geometry.distance(river))
        if d > 3000:
            continue
        m = rasterio.features.geometry_mask([u.geometry], out_shape=dem.shape, transform=tr, invert=True, all_touched=True)
        z = dem[m & np.isfinite(dem)]
        if z.size < 3:
            continue
        row = dict(id_poligono=int(i), densidade=u.get("Densidade"), area_km2=round(u.area_km2, 3), dist_ao_rio_m=round(d),
                   alt_min_m=round(float(z.min()), 1), alt_p10_m=round(float(np.percentile(z, 10)), 1),
                   alt_mediana_m=round(float(np.median(z)), 1), alt_max_m=round(float(z.max()), 1))
        c = u.geometry.representative_point()
        for k, (line, km_z, z_z) in profiles.items():
            if u.geometry.distance(line) > 3000:  # mancha longe deste trecho: não comparar com a cota dele
                continue
            s = line.project(c) / 1000
            cota = float(np.interp(s, km_z, z_z))
            row[f"cota_agua_{k}_m"] = round(cota, 1)
            row[f"folga_{k}_m"] = round(row["alt_min_m"] - cota, 1)  # >0: ponto mais baixo da mancha urbana fica ACIMA da cota máx.
            row[f"pct_celulas_abaixo_cota_{k}"] = round(100 * float((z <= cota).mean()), 1)
        rows.append(row)
    return pd.DataFrame(share), pd.DataFrame(rows).sort_values("area_km2", ascending=False)


# ---------------------------------------------------------------- tempo
def rise_times() -> pd.DataFrame:
    """Só o que os PAEs documentam: tempo até a chegada e até o pico, por seção. A DESCIDA (e logo a duração) não é tabelada."""
    rows = []
    for tr in (10000, 10):
        s = D.sections("PIR", {10000: "ruptura_tr10000", 10: "ruptura_tr10"}[tr])
        s = s[s.secao != "ST-00"]
        rows += [dict(barragem="Piraju", cenario=f"ruptura TR {tr}", secao=r.secao, km=r.distancia_km, chegada_min=r.t_frente_min,
                      pico_min=r.t_pico_min, subida_ate_o_pico_min=r.t_pico_min - r.t_frente_min) for _, r in s.iterrows()]
    return pd.DataFrame(rows)


def mass_bound() -> pd.DataFrame:
    """TETO por conservação de massa (não é estimativa de duração): a água liberada não passa do volume do reservatório,
    logo a vazão não fica Δ acima da base por mais de V/Δ. Piraju: V = 105,58 hm³ (PAE p. 14). Jurumirim: V total 7.007,52 hm³
    (o volume acima do fundo da brecha não consta do PAE, então o teto é frouxo)."""
    rows = []
    for nome, v_hm3 in (("Piraju", 105.58), ("Jurumirim", 7007.52)):
        for delta in (1000, 2000, 5000, 10000):
            rows.append(dict(barragem=nome, volume_hm3=v_hm3, delta_m3s=delta, teto_horas=round(v_hm3 * 1e6 / delta / 3600, 1)))
    return pd.DataFrame(rows)
