"""Tests to check annotation consistency
"""
from __future__ import print_function

import unittest
import csv
import os
import glob
import numpy as np

from medleydb import AUDIO_AVAILABLE
from medleydb import ANNOT_PATH
from medleydb import MultiTrack
from medleydb import TRACK_LIST_V1
from medleydb.annotate import melody as G
from medleydb import multitrack


def array_almost_equal(array1, array2, tolerance=1e-7):
    diff = np.abs(array1 - array2)
    num_not_equal = diff > tolerance
    print("number of unequal elements: %s" % np.sum(num_not_equal))
    return np.sum(num_not_equal) == 0


class TestFileNames(unittest.TestCase):
    def setUp(self):
        self.track_list = TRACK_LIST_V1

    def test_annotation_folders_exist(self):
        self.assertTrue(os.path.exists(ANNOT_PATH))
        self.assertTrue(os.path.exists(multitrack._ACTIVATION_CONF_PATH))
        self.assertTrue(os.path.exists(multitrack._MELODY_PATH))
        self.assertTrue(os.path.exists(multitrack._INTERVALS_PATH))
        self.assertTrue(os.path.exists(multitrack._MELODY1_PATH))
        self.assertTrue(os.path.exists(multitrack._MELODY2_PATH))
        self.assertTrue(os.path.exists(multitrack._MELODY3_PATH))
        self.assertTrue(os.path.exists(multitrack._RANKING_PATH))
        self.assertTrue(os.path.exists(multitrack._PITCH_PATH))
        self.assertTrue(os.path.exists(multitrack._PITCH_PYIN_PATH))
        self.assertTrue(os.path.exists(multitrack._SOURCEID_PATH))

    def test_activation_conf_names(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            if not mtrack.has_bleed:
                self.assertTrue(os.path.exists(mtrack.activation_conf_fpath))

    def test_sourceid_names(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            print(mtrack.source_id_fpath)
            self.assertTrue(os.path.exists(mtrack.source_id_fpath))


@unittest.skipIf(not AUDIO_AVAILABLE, "requires audio access")
class TestMelodyAnnotations(unittest.TestCase):
    def setUp(self):
        self.track_list = TRACK_LIST_V1

    def test_melody_annotations(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            if not mtrack.has_melody or mtrack.duration is None:
                continue

            generated_melody1 = G.create_melody1_annotation(mtrack)
            actual_melody1 = mtrack.melody1_annotation
            self.assertTrue(
                array_almost_equal(actual_melody1, generated_melody1)
            )

            generated_melody2 = G.create_melody2_annotation(mtrack)
            actual_melody2 = mtrack.melody2_annotation
            self.assertTrue(
                array_almost_equal(actual_melody2, generated_melody2)
            )

            generated_melody3 = G.create_melody3_annotation(mtrack)
            actual_melody3 = mtrack.melody3_annotation
            self.assertTrue(
                array_almost_equal(actual_melody3, generated_melody3)
            )


class TestRankingAnnotations(unittest.TestCase):
    def setUp(self):
        self.track_list = TRACK_LIST_V1

    def test_rankings(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            rankings = list(mtrack.melody_rankings.values())
            # test that there are no duplicate rankings
            self.assertTrue(len(rankings) == len(set(rankings)))
            # test that rankings start at 1 and go up by step
            self.assertTrue(
                sorted(rankings) == list(range(1, len(rankings) + 1))
            )


class TestPitchAnnotations(unittest.TestCase):

    def setUp(self):
        pitch_path = multitrack._PITCH_PATH
        self.pitch_files = glob.glob(os.path.join(pitch_path, '*.*'))

    def test_extension(self):
        for fpath in self.pitch_files:
            ext = os.path.basename(fpath).split('.')[-1]
            self.assertEqual(ext, 'csv')

    def test_delimiter(self):
        for fpath in self.pitch_files:
            with open(fpath, 'r') as fhandle:
                reader = csv.reader(fhandle, delimiter=',')
                for line in reader:
                    self.assertTrue(len(line) > 1)
                    break
