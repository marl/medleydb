import medleydb as mdb


def test_all():
    assert len(mdb.load_all_multitracks()) > 0


def test_melody():
    assert len(mdb.load_melody_multitracks()) > 0
