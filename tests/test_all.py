import medleydb as mdb


def test_all():
    assert len(list(mdb.load_all_multitracks())) > 0


def test_melody():
    assert len(list(mdb.load_melody_multitracks())) > 0
