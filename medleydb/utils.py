#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utilities to navigate MedleyDB.
"""

import glob
import os
from . import multitrack as M
from . import sox
from . import AUDIO_DIR


def load_melody_multitracks():
    """Load all multitracks that have melody annotations.

    Example:
        >>> melody_multitracks = load_melody_multitracks()

    Returns:
        melody_multitracks (list): List of multitrack objects.

    """
    multitracks = load_all_multitracks()
    for track in multitracks:
        if track.melody1_annotation:
            yield track


def load_all_multitracks():
    """Load all multitracks in AUDIO_DIR.

    Example:
        >>> multitracks = load_all_multitracks()

    Returns:
        multitracks (list): List of multitrack objects.

    """
    track_list = glob.glob(os.path.join(AUDIO_DIR, '*'))
    multitracks = load_multitracks(track_list)
    return multitracks


def load_multitracks(track_list):
    """Load a list of multitracks.

    Example:
        # create a list of paths to multitrack directories
        >>> track_list = ['path/to/ArtistName1_TrackName1', \
                          'path/to/ArtistName2_TrackName2', \
                          'path/to/ArtistName3_TrackName3']
        >>> multitracks = load_multitracks(track_list)

    Args:
        track_list (list): List of paths to multi-track folders.

    Returns:
        multitracks (dict): List of multitrack objects.

    """
    for multitrack in track_list:
        yield M.MultiTrack(multitrack)


def get_files_for_instrument(instrument, multitrack_list=None):
    """Get all (stem) files for a particular instrument from the dataset.

    Examples:
        # load drum set files from the full dataset:
        >>> drumset_files = get_files_for_instrument('drum set')

        # load violin files from a subset of the dataset:
        >>> track_list = ['path/to/ArtistName1_TrackName1', \
                          'path/to/ArtistName2_TrackName2', \
                          'path/to/ArtistName3_TrackName3']
        >>> multitrack_subset = load_multitracks(track_list)
        >>> violin_files = get_files_for_instrument(
                'violin', multitrack_subset
            )

    Args:
        instrument (str): Instrument files to extract.
        multitrack_list (list of MultiTracks, optional):
            List of MultiTrack objects.
            If None, uses all multitracks.

    Returns:
        inst_list (list): List of filepaths corresponding to instrument label.

    """
    assert M.is_valid_instrument(instrument), \
        "%s is not in the instrument taxonomy." % instrument

    if not multitrack_list:
        multitrack_list = load_all_multitracks()

    for multitrack in multitrack_list:
        for stem in multitrack.stems:
            if stem.instrument == instrument:
                yield stem.file_path


def preview_audio(multitrack, selection='all', preview_length=8):
    """Listen to a preview of the audio for a particular multitrack.

    Examples:
        # Preview audio from a MultiTrack object.
        >>> mtrack = medleydb.MultiTrack('/path/to/ArtistName_TrackName')
        >>> preview_audio(mtrack)

        # Preview only the stems from a path to a multitrack.
        >>> preview_audio('/path/to/ArtistName_TrackName', selection='stems')

    Args:
        multitrack (MultiTrack or str): An instance of the class MultiTrack or
            a path to a multitrack folder.
        selection (str, optional): Determines which audio to play.
            'all' plays mix, stems, and raw.
            'stems' plays only the stems.
            'raw' plays only the raw audio.
            'mix' plays only the mix.
        preview_length (float, optional): Number of seconds to preview.

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
