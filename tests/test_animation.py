from jurumirim import animation, data


def test_frame_documented_banner_and_reached_logic(tmp_path):
    fig = animation.frame(60)
    texts = " ".join(t.get_text() for t in fig.axes[0].texts)
    assert "sem interpolação" in texts
    s = data.sections()
    assert (s.tempo_chegada_min <= 60).sum() == 9  # ST-001..ST-009 (<= 00:56)


def test_interpolated_frame_is_labeled():
    fig = animation.frame(60, interpolate=True)
    assert "INTERPOLAÇÃO ILUSTRATIVA" in " ".join(t.get_text() for t in fig.axes[0].texts)


def test_export_few_frames(tmp_path):
    ps = animation.export_frames(tmp_path, times=[0, 30, 120])
    assert len(ps) == 3 and all(p.exists() for p in ps)
