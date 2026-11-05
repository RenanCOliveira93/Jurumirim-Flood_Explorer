import geopandas as gpd
import numpy as np
import pytest
from pyproj import CRS
from shapely.geometry import box

from jurumirim import gis
from jurumirim.georef import fit_transform, pt_to_utm, utm_to_pt
from jurumirim.paths import PROCESSED


@pytest.fixture(scope="module")
def polys():
    return gpd.read_file(PROCESSED / "pae_flood_polygons.gpkg", layer="manchas")


def test_georef_rms_subpixel():
    A, info = fit_transform()
    assert info["rms_m"] < 1.0 and info["n_control_points"] == 36
    assert abs(info["scale_x_m_per_pt"] - info["scale_y_m_per_pt"]) < 0.01  # ~isotrópico


def test_roundtrip_pt_utm():
    A, _ = fit_transform()
    e, n = pt_to_utm(A, [100.0, 900.0], [200.0, 1200.0])
    x, y = utm_to_pt(A, e, n)
    assert np.allclose(x, [100, 900]) and np.allclose(y, [200, 1200])


def test_crs_is_projected_utm22s(polys):
    assert CRS(polys.crs).to_epsg() == 31982 and polys.crs.is_projected


def test_geometries_valid_and_nonempty(polys):
    assert polys.geometry.is_valid.all() and (~polys.geometry.is_empty).all()
    assert set(polys.classe) >= {"ZAS", "ZSS", "ENVOLTORIA_RUPTURA", "CHEIA_SR"}


def test_areas_plausible_and_consistent(polys):
    a = polys.groupby("classe").geometry.apply(lambda g: g.area.sum() / 1e6)
    assert 5 < a["ZAS"] < 9          # ZAS ~6,8 km2 (ordem de grandeza; extensão 6,71 km)
    assert 25 < a["ENVOLTORIA_RUPTURA"] < 36
    assert a["ENVOLTORIA_RUPTURA"] == pytest.approx(a["ZAS"] + a["ZSS_APENAS"], rel=0.02)


def test_sections_fall_inside_or_near_envelope(polys):
    sec = gpd.read_file(PROCESSED / "pae_flood_polygons.gpkg", layer="secoes")
    env = polys[polys.classe == "ENVOLTORIA_RUPTURA"].geometry.iloc[0]
    d = sec.geometry.distance(env)
    assert (d < 150).all()  # ponto central da seção está sobre a mancha (±incerteza)


def test_area_calculation_requires_projected_crs():
    mun = gpd.GeoDataFrame({"nome": ["x"], "codarea": ["1"]}, geometry=[box(-49, -23, -48.9, -22.9)], crs=4326)
    with pytest.raises(AssertionError):
        gis.municipality_overlap(box(0, 0, 1, 1), mun)


def test_overlap_known_geometry():
    mun = gpd.GeoDataFrame({"nome": ["m"], "codarea": ["1"]}, geometry=[box(0, 0, 1000, 1000)], crs=31982)
    out = gis.municipality_overlap(box(500, 0, 1500, 1000), mun)
    assert out.area_envoltoria_no_municipio_km2.iloc[0] == pytest.approx(0.5)
    assert out.pct_do_municipio.iloc[0] == pytest.approx(50.0)


def test_no_overlap_returns_empty():
    mun = gpd.GeoDataFrame({"nome": ["m"], "codarea": ["1"]}, geometry=[box(0, 0, 10, 10)], crs=31982)
    assert gis.municipality_overlap(box(100, 100, 200, 200), mun).empty


def test_piraju_overlap_outputs_exist_and_urban_outside():
    import pandas as pd
    uo = pd.read_csv(PROCESSED / "overlap_urbanizadas.csv")
    piraju = uo[uo.municipio == "Piraju"]
    assert len(piraju) > 0
    assert (piraju.distancia_a_envoltoria_m >= 0).all()


def test_urban_summary_facts():
    from jurumirim import data
    us = data.urban_summary()
    assert not us["main_intersects"] and us["main_distance_m"] > 1000     # maior mancha urbana fora da envoltória
    assert us["n_intersecting"] == 2 and us["intersecting_area_km2"] < 0.01  # sobreposição marginal, documentada
    assert all(p["pct_na_envoltoria"] < 2 for p in us["intersecting_polygons"])
