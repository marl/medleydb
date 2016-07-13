#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utilities to navigate MedleyDB.
"""

from __future__ import print_function

from . import multitrack as M
from . import TRACK_LIST


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
    multitracks = load_multitracks(TRACK_LIST)
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
