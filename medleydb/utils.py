#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utilities to navigate MedleyDB.
"""

from __future__ import print_function

from . import multitrack as M
from . import TRACK_LIST_V1
from . import ARTIST_INDEX

import numpy as np
from sklearn.cross_validation import ShuffleSplit


def load_melody_multitracks():
    """Load all multitracks that have melody annotations.

    Returns
    -------
    melody_multitracks : list
        List of multitrack objects.

    Examples
    --------
    >>> melody_multitracks = load_melody_multitracks()

    """
    multitracks = load_all_multitracks()
    for track in multitracks:
        if track.has_melody:
            yield track


def load_all_multitracks():
    """Load all multitracks in MEDLEYDB_PATH.

    Returns
    -------
    multitracks : list
        List of multitrack objects.

    Examples
    --------
    >>> multitracks = load_all_multitracks()

    """
    multitracks = load_multitracks(TRACK_LIST_V1)
    return multitracks


def load_multitracks(track_list):
    """Load a list of multitracks.

    Parameters
    ----------
    track_list : list
        List of track ids in format 'Artist_Title'

    Returns
    -------
    multitracks : dict
        List of multitrack objects.

    Examples
    --------
    >>> track_list = ['ArtistName1_TrackName1', \
                      'ArtistName2_TrackName2', \
                      'ArtistName3_TrackName3']
    >>> multitracks = load_multitracks(track_list)

    """
    for track_id in track_list:
        yield M.MultiTrack(track_id)


def get_files_for_instrument(instrument, multitrack_list=None):
    """Get all (stem) files for a particular instrument from the dataset.

    Parameters
    ----------
    instrument : str
        Instrument files to extract.
    multitrack_list : list of MultiTrack objects or None, default=None
        List of MultiTrack objects.
        If None, uses all multitracks.

    Returns
    -------
    inst_list : list
        List of filepaths corresponding to instrument label.

    Examples
    --------
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

    """
    if not M.is_valid_instrument(instrument):
        raise ValueError("%s is not in the instrument taxonomy." % instrument)

    if not multitrack_list:
        multitrack_list = load_all_multitracks()

    for multitrack in multitrack_list:
        for stem in multitrack.stems.values():
            if stem.instrument == instrument:
                yield stem.audio_path


def artist_conditional_split(trackid_list=None, test_size=0.15, num_splits=5,
                             random_state=None, artist_index=None):
    """Create artist-conditional train-test splits.
    The same artist (as defined by the artist_index) cannot appear
    in both the training and testing set.

    Parameters
    ----------
    trackid_list : list or None, default=None
        List of trackids to use in train-test split. If None, uses all tracks
    test_size : float, default=0.15
        Fraction of tracks to use in test set. The test set will be as close
        as possible in size to this value, but it may not be exact due to the
        artist-conditional constraint.
    num_splits : int, default=5
        Number of random splits to create
    random_state : int or None, default=None
        A random state to optionally reproduce the same random split.
    artist_index : dict or None, default=None
        Dictionary mapping each track id in trackid_list to a string that
        uniquely identifies each artist.
        If None, uses the predefined index ARTIST_INDEX.

    Returns
    -------
    splits : list of dicts
        List of length num_splits of train/test split dictionaries. Each
        dictionary has the keys 'train' and 'test', each which map to lists of
        trackids.

    """
    if trackid_list is None:
        trackid_list = TRACK_LIST_V1

    if artist_index is None:
        artist_index = ARTIST_INDEX

    artists = np.asarray([ARTIST_INDEX[trackid] for trackid in trackid_list])

    splitter = _ShuffleLabelsOut(
        artists, random_state=random_state, test_size=test_size,
        n_iter=num_splits
    )

    trackid_array = np.array(trackid_list)
    splits = []
    for train, test in splitter:
        splits.append({
            'train': list(trackid_array[train]),
            'test': list(trackid_array[test])
        })

    return splits


class _ShuffleLabelsOut(ShuffleSplit):
    '''Shuffle- Labels-Out cross-validation iterator

    Parameters
    ----------
    y :  array, [n_samples]
        Labels of samples

    n_iter : int (default 5)
        Number of shuffles to generate

    test_size : float (default 0.2), int, or None

    train_size : float, int, or None (default is None)

    random_state : int or RandomState
    '''

    def __init__(self, y, n_iter=5, test_size=0.2, train_size=None,
                 random_state=None):

        classes, y_indices = np.unique(y, return_inverse=True)

        super(_ShuffleLabelsOut, self).__init__(
            len(classes), n_iter=n_iter, test_size=test_size,
            train_size=train_size, random_state=random_state
        )

        self.classes = classes
        self.y_indices = y_indices

    def __repr__(self):
        return ('%s(labels=%s, n_iter=%d, test_size=%s, '
                'random_state=%s)' % (
                    self.__class__.__name__,
                    self.y_indices,
                    self.n_iter,
                    str(self.test_size),
                    self.random_state,
                ))

    def __len__(self):
        return self.n_iter

    def _iter_indices(self):

        for y_train, y_test in super(_ShuffleLabelsOut, self)._iter_indices():
            # these are the indices of classes in the partition
            # invert them into data indices

            train = np.flatnonzero(np.in1d(self.y_indices, y_train))
            test = np.flatnonzero(np.in1d(self.y_indices, y_test))

            yield train, test
