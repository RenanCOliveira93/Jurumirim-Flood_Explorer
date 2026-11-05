"""Posiciona seções por distância ao longo do eixo do rio (OSM). Resultado: ILUSTRAÇÃO, não georreferenciamento do PAE."""
from __future__ import annotations

import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union

CRS = "EPSG:31982"
_TO_UTM = Transformer.from_crs(4326, 31982, always_xy=True)


def river_line(waterways_json: Path, name: str = "Rio Paranapanema") -> LineString:
    """Une as vias OSM com `name` numa única linha em UTM 22S (assert: resultado contínuo)."""
    d = json.loads(Path(waterways_json).read_text())
    parts = [LineString([_TO_UTM.transform(p["lon"], p["lat"]) for p in e["geometry"]])
             for e in d["elements"] if e.get("tags", {}).get("name") == name and len(e.get("geometry", [])) >= 2]
    if not parts:
        raise ValueError(f"nenhuma via OSM chamada {name!r}")
    merged = linemerge(unary_union(parts))
    if merged.geom_type != "LineString":
        merged = max(merged.geoms, key=lambda g: g.length)  # maior trecho contínuo
    return merged


def place(river: LineString, origin: Point, distances_km, downstream_positive: bool = True) -> dict:
    """Pontos a `d` km do `origin` projetado no eixo. `downstream_positive`: sentido crescente da linha = jusante."""
    s0 = river.project(origin)
    sign = 1 if downstream_positive else -1
    pts = []
    for d in distances_km:
        s = s0 + sign * d * 1000
        if not 0 <= s <= river.length:
            raise ValueError(f"distância {d} km fora do eixo do rio")
        p = river.interpolate(s)
        pts.append((p.x, p.y))
    return dict(points=pts, origin_offset_m=float(river.distance(origin)), s0_m=float(s0))
