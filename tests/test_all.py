import medleydb as mdb


def test_all():
    assert next(mdb.load_all_multitracks())


def test_melody():
    assert next(mdb.load_melody_multitracks())
