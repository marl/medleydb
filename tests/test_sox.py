import medleydb as mdb
from medleydb import sox

def noop(*args, **kwargs):
    pass


def test_preview(monkeypatch):
    monkeypatch.setattr(sox, "quick_play", noop)
    track = mdb.load_all_multitracks()[0]
    mdb.preview_audio(track)


# TODO: Actually test sox. This test only tests the preview_audio()
# function by mocking the sox module (replacing sox.quick_play()
# with a function that does nothing)
