""" Utilities to navigate MedleyDB.
"""

import glob
import os
from . import multitrack as M
from . import sox
from . import AUDIO_DIR


def load_melody_multitracks():
    """Load all multitracks that have melody annotations.

    Returns
    -------
    melody_multitracks : list
        List of multitrack objects.    
    """
    multitracks = load_all_multitracks()
    return [track for track in multitracks if track.melody1_annotation]


def load_all_multitracks():
    """Load all multitracks in AUDIO_DIR.

    Returns
    -------
    multitracks : list
        List of multitrack objects.
    """
    track_list = glob.glob(os.path.join(AUDIO_DIR, '*'))
    multitracks = load_multitracks(track_list)
    return multitracks


def load_multitracks(track_list):
    """Load a list of multitracks.
    Parameters
    ----------
    track_list : list
        List of paths to multi-track folders.

    Returns
    -------
    multitracks : dict
        List of multitrack objects.
    """
    multitracks = []
    for multitrack in track_list:
        mtrack = M.MultiTrack(multitrack)
        multitracks.append(mtrack)
    return multitracks


def get_files_for_instrument(instrument, multitracks=None):
    """Get all (stem) files for a particular instrument from the dataset.

    Parameters
    ----------
    instrument : str
        Instrument files to extract.
    multitracks : str
        Dataset directory.

    Returns
    -------
    file_list : list
        List of filepaths corresponding to an instrument label.
    """
    assert M.is_valid_instrument(instrument), \
            "%s is not in the instrument taxonomy" % instrument

    if not multitracks:
        multitracks = load_all_multitracks()

    file_list = []
    for multitrack in multitracks:
        for stem in multitrack.stems:
            if stem.instrument == instrument:
                file_list.append(stem.file_path)
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

    if selection == 'all' or selection == 'mix':
        print "Previewing the mix..."
        sox.quick_play(mix, duration=preview_length)

    if selection == 'all' or selection == 'stems':
        for track in stems:
            print "Previewing stem %r (%s)..." \
                % (track.stem_idx, track.instrument)
            sox.quick_play(track.file_path, duration=preview_length)

    if selection == 'all' or selection == 'raw':
        for track in raw_audio:
            print "Previewing raw audio %r %r (%s)..." \
                % (track.stem_idx, track.raw_idx, track.instrument)
            sox.quick_play(track.file_path, duration=preview_length)
