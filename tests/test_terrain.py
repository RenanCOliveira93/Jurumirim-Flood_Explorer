import numpy as np

from jurumirim.terrain import hillshade, sample_dem


def test_dem_values_plausible_for_region():
    z = sample_dem([667050.0, 681083.0], [7436709.0, 7432016.0])
    assert np.isfinite(z).all() and ((z > 450) & (z < 800)).all()


def test_dem_outside_extent_is_nan_or_nodata():
    z = sample_dem([100000.0], [100000.0])
    assert z.shape == (1,)


def test_hillshade_range():
    z = np.add.outer(np.arange(20.0), np.arange(20.0))
    h = hillshade(z, 30, 30)
    assert h.min() >= 0 and h.max() <= 1
