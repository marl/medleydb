import pytest
import medleydb.sql as m


@pytest.fixture
def track(session):
    return session.query(m.model.Track).first()


# Test if hybrid_properies work
def test_hybrid_properies(track):
    repr(track.composers[0])
    repr(track.producers[0])

    repr(track.stems[0])
    track.stems[0].audio_path
    track.stems[0].audio_data
    track.stems[0].annotation_path
    track.stems[0].rank

    repr(track.stems[0].instrument)

    repr(track.stems[0].instrument.taxon)

    repr(track.stems[0].raws[0])
    track.stems[0].raws[0].audio_path
    track.stems[0].raws[0].audio_data

    repr(track.melodies[0])
    track.melodies[0].annotation_path
    track.melodies[0].annotation_data

    repr(track)
    track.audio_path
    track.audio_data
    track.pitch_data
    track.base_dir
    track.track_id
    track.metadata_path
