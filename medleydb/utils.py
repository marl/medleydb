""" Utilities to navigate MedleyDB.
"""

import glob
import os
from . import multitrack as M
from . import sox
from . import AUDIO_DIR


def load_dataset():
    """Load the dataset to a dictionary.
    Parameters
    ----------
    medleydb_dir : str
        Directory containing dataset.

    Returns
    -------
    dataset : dict
        Dictionary keyed by artist_track. Values are multitrack objects.
    """
    track_list = glob.glob(os.path.join(AUDIO_DIR, '*'))
    dataset = load_tracks(track_list)
    return dataset


def load_tracks(track_list):
    """Load a list of tracks to a dictionary.
    Parameters
    ----------
    track_list : list
        List of paths to track folders.

    Returns
    -------
    tracks : dict
        Dictionary keyed by artist_track. Values are multitrack objects.
    """
    tracks = {}
    for track in track_list:
        mtrack = M.MultiTrack(track)
        tracks[mtrack.track_id] = mtrack
    return tracks


def get_files_for_instrument(instrument, dataset=None):
    """Get all (stem) files for a particular instrument from the dataset.

    Parameters
    ----------
    instrument : str
        Instrument files to extract.
    audio_dir : str
        Dataset directory.

    Returns
    -------
    file_list : list
        List of filepaths corresponding to an instrument label.
    """
    assert M.is_valid_instrument(instrument), "invalid instrument"

    if not dataset:
        dataset = load_dataset()

    file_list = []
    for song in dataset:
        for track in dataset[song].stems:
            if track.instrument == instrument:
                file_list.append(track.file_path)
    return file_list


def preview_audio(multitrack, selection='all', preview_length=8):
    """Listen to a preview of the audio for a particular multitrack.

    Parameters
    ----------
    multitrack : MultiTrack or str
        An instance of the class MultiTrack or a path to a multitrack folder.
    selection : str
        Determines which audio to play.
            'all' plays mix, stems, and raw.
            'stems' plays only the stems.
            'raw' plays only the raw audio.
            'mix' plays only the mix.
    preview_length : float
        Number of seconds of audio to preview.
    """

    if isinstance(multitrack, M.MultiTrack):
        mtrack = multitrack
    elif isinstance(multitrack, str) and os.path.exists(multitrack):
        mtrack = M.MultiTrack(multitrack)

    raw_audio = mtrack.raw_audio
    stems = mtrack.stems
    mix = mtrack.mix_path

    if selection is 'all' or selection is 'mix':
        print "Previewing the mix..."
        sox.quick_play(mix, duration=preview_length)

    if selection is 'all' or selection is 'stems':
        for track in stems:
            print "Previewing stem %r (%s)..." \
                % (track.stem_idx, track.instrument)
            sox.quick_play(track.file_path, duration=preview_length)

    if selection is 'all' or selection is 'raw':
        for track in raw_audio:
            print "Previewing raw audio %r %r (%s)..." \
                % (track.stem_idx, track.raw_idx, track.instrument)
            sox.quick_play(track.file_path, duration=preview_length)
