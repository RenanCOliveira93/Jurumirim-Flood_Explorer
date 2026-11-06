#!/usr/bin/env python
"""Gera data/processed/dams/exposure/*.csv: força (v, h·v), extensão lateral, % de área urbanizada, altitude e tempos.
Tudo DERIVADO DO PAE (valores tabelados) ou ESTIMATIVA EXPLORATÓRIA (mancha estimada de Piraju). Ver src/jurumirim/exposure.py."""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.ops import substring, unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jurumirim import bathtub as B, data, dams as D, exposure as X, gis  # noqa: E402

X.OUT.mkdir(parents=True, exist_ok=True)

# eixos
rx, ry = D.river_xy()
full = __import__("shapely").geometry.LineString(list(zip(rx, ry)))
pts = D.dam_points().set_index("dam")
line_jur = substring(full, 0, full.project(Point(pts.loc["PIR", "x_utm"], pts.loc["PIR", "y_utm"])))
line_pir = B._downstream_line("PIR", 33.0)
water = unary_union(list(gis.load_water().geometry.make_valid()))

# mancha por cenário
p = data.polygons()
polys = {
    "JUR oficial (envoltória ZAS+ZSS, PAE p. 38)": (data.envelope(), line_jur),
    "JUR oficial (só ZAS)": (unary_union(list(p[p.classe == "ZAS"].geometry)), line_jur),
}
est = gpd.read_file(D.DAMS_DIR / "PIR" / "estimativa_mancha.gpkg")
for tipo in ("ruptura", "natural"):
    for tr in (10000, 10):
        g = est[(est.tipo == tipo) & (est.tr_anos == tr)]
        polys[f"PIR estimativa {tipo} TR {tr}"] = (unary_union(list(g.geometry)), line_pir)

# 1) força
force = X.force_table(); force.round(3).to_csv(X.OUT / "forca.csv", index=False)

# 2) extensão lateral
tr_rows = []
for k, (poly, line) in polys.items():
    t = X.lateral(poly, water, line); t.insert(0, "cenario", k); tr_rows.append(t)
lat = pd.concat(tr_rows, ignore_index=True); lat.to_csv(X.OUT / "lateral_transectos.csv", index=False)
X.lateral_summary(lat).to_csv(X.OUT / "lateral_resumo.csv", index=False)

# 3) área urbana + altitude
prof = {}
for tipo, getter in (("ruptura", lambda tr: D.sections("PIR", "ruptura_tr10000")), ("natural", lambda tr: D.natural_sections(10000))):
    s = getter(10000); s = s[s.secao != "ST-00"].dropna(subset=["elev_max_m"])
    prof[f"{tipo}_tr10000"] = (line_pir, s.distancia_km.to_numpy(float), s.elev_max_m.to_numpy(float))
share, alt = X.urban_exposure({k: v[0] for k, v in polys.items()},
                              {"jur": line_jur, "pir": line_pir}, prof)
share.to_csv(X.OUT / "urbana_pct.csv", index=False); alt.to_csv(X.OUT / "urbana_altitude.csv", index=False)

# 4) tempo
X.rise_times().to_csv(X.OUT / "tempo_subida.csv", index=False)
X.mass_bound().to_csv(X.OUT / "tempo_teto_massa.csv", index=False)
pd.set_option("display.width", 220, "display.max_columns", 30)
print(pd.read_csv(X.OUT / "lateral_resumo.csv").to_string()); print(share.to_string()); print(alt.head(8).to_string())
