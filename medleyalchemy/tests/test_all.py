import pytest
import medleyalchemy as m


@pytest.fixture
def session():
    return m.session("database.sql")


@pytest.fixture
def track(session):
    return session.query(m.model.Track).first()


# Test if hybrid_properies work
def test_hybrid_properies(track):
    track.stems[0].path
    track.stems[0].data
    track.stems[0].raws[0].path
    track.stems[0].raws[0].data
    track.melodies[0].path
    track.melodies[0].data
    track.data
    track.data_path
    track.mix_path
    track.metadata_path
