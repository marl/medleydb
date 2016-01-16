#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utilities to navigate MedleyDB.
"""

from . import multitrack as M
from . import sox
from . import TRACK_LIST


def load_track_list():
    """ Load the list of tracks in the current version of MedleyDB.

    Example:
        >>> track_list = load_track_list()

    Returns:
        track_list (list): List of track id strings in format "Artist_Title"

    """
    track_list = []
    with open(TRACK_LIST, 'r') as fhandle:
        for line in fhandle.readlines():
            track_list.append(line.strip('\n'))
    return track_list


def load_melody_multitracks():
    """Load all multitracks that have melody annotations.

    Example:
        >>> melody_multitracks = load_melody_multitracks()

    Returns:
        melody_multitracks (list): List of multitrack objects.

    """
    multitracks = load_all_multitracks()
    for track in multitracks:
        if track.has_melody:
            yield track


def load_all_multitracks():
    """Load all multitracks in MEDLEYDB_PATH.

    Example:
        >>> multitracks = load_all_multitracks()

    Returns:
        multitracks (list): List of multitrack objects.

    """
    track_list = load_track_list()
    multitracks = load_multitracks(track_list)
    return multitracks


def load_multitracks(track_list):
    """Load a list of multitracks.

    Example:
        # create a list of paths to multitrack directories
        >>> track_list = ['ArtistName1_TrackName1', \
                          'ArtistName2_TrackName2', \
                          'ArtistName3_TrackName3']
        >>> multitracks = load_multitracks(track_list)

    Args:
        track_list (list): List of track ids in format 'Artist_Title'

    Returns:
        multitracks (dict): List of multitrack objects.

    """
    for track_id in track_list:
        yield M.MultiTrack(track_id)


def get_files_for_instrument(instrument, multitrack_list=None):
    """Get all (stem) files for a particular instrument from the dataset.

    Examples:
        # load drum set files from the full dataset:
        >>> drumset_files = get_files_for_instrument('drum set')

        # load violin files from a subset of the dataset:
        >>> track_list = ['ArtistName1_TrackName1', \
                          'ArtistName2_TrackName2', \
                          'ArtistName3_TrackName3']
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
    if not M.is_valid_instrument(instrument):
        raise ValueError("%s is not in the instrument taxonomy." % instrument)

    if not multitrack_list:
        multitrack_list = load_all_multitracks()

    for multitrack in multitrack_list:
        for stem in multitrack.stems.values():
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
            a track id.
        selection (str, optional): Determines which audio to play.
            'all' plays mix, stems, and raw.
            'stems' plays only the stems.
            'raw' plays only the raw audio.
            'mix' plays only the mix.
        preview_length (float, optional): Number of seconds to preview.

    """

    if isinstance(multitrack, M.MultiTrack):
        mtrack = multitrack
    elif isinstance(multitrack, str):
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
