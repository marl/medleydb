import unittest
import os
import glob
import numpy as np

from medleydb import AUDIO_AVAILABLE
from medleydb import ANNOT_PATH
from medleydb import MultiTrack
from medleydb import TRACK_LIST
from medleydb.annotate import generate_melody_annotations as G


def array_almost_equal(array1, array2, tolerance=1e-7):
    diff = np.abs(array1 - array2)
    num_not_equal = diff > tolerance
    print("number of unequal elements: %s" % np.sum(num_not_equal))
    return np.sum(num_not_equal) == 0


class TestFileNames(unittest.TestCase):
    def setUp(self):
        self.track_list = TRACK_LIST
        self.folders = set(
            glob.glob(os.path.join(ANNOT_PATH, "*_ANNOTATIONS"))
        )
        self.annot_fmt = "%s_ANNOTATIONS"

    def test_tracks_have_annotation_folders(self):
        for track in self.track_list:
            expected_folder_name = self.annot_fmt % track
            expected_folder_path = os.path.join(
                ANNOT_PATH, expected_folder_name
            )
            self.assertTrue(os.path.exists(expected_folder_path))

    def test_pitch_folder_names(self):
        for track in self.track_list:
            pitch_folder = os.path.join(
                ANNOT_PATH, self.annot_fmt % track, "*_PITCH"
            )
            expected_pitch_folder = os.path.join(
                ANNOT_PATH, self.annot_fmt % track, "%s_PITCH" % track
            )
            actual_pitch_folder = glob.glob(pitch_folder)
            if len(actual_pitch_folder) > 0:
                actual_pitch_folder = actual_pitch_folder[0]
                self.assertEqual(expected_pitch_folder, actual_pitch_folder)
            else:
                print(("[%s] Pitch folder missing " % track))

    def test_activation_conf_names(self):
        for track in self.track_list:
            activation_conf_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_ACTIVATION_CONF.lab"
                )
            )
            expected_activation_conf = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_ACTIVATION_CONF.lab" % track
            )
            if len(activation_conf_glob) > 0:
                actual_activation_conf = activation_conf_glob[0]
                self.assertEqual(
                    expected_activation_conf, actual_activation_conf
                )
            else:
                print(("[%s] Activation confidence missing " % track))

    def test_intervals_names(self):
        for track in self.track_list:
            intervals_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_INTERVALS.txt"
                )
            )
            expected_intervals = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_INTERVALS.txt" % track
            )
            if len(intervals_glob) > 0:
                actual_intervals = intervals_glob[0]
                self.assertEqual(
                    expected_intervals, actual_intervals
                )
            else:
                print(("[%s] Intervals file missing " % track))

    def test_melody1_names(self):
        for track in self.track_list:
            melody1_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_MELODY1.csv"
                )
            )
            expected_melody1 = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_MELODY1.csv" % track
            )
            if len(melody1_glob) > 0:
                actual_melody1 = melody1_glob[0]
                self.assertEqual(
                    expected_melody1, actual_melody1
                )
            else:
                print(("[%s] Melody1 missing " % track))

    def test_melody2_names(self):
        for track in self.track_list:
            melody2_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_MELODY2.csv"
                )
            )
            expected_melody2 = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_MELODY2.csv" % track
            )
            if len(melody2_glob) > 0:
                actual_melody2 = melody2_glob[0]
                self.assertEqual(
                    expected_melody2, actual_melody2
                )
            else:
                print(("[%s] Melody2 missing " % track))

    def test_melody3_names(self):
        for track in self.track_list:
            melody3_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_MELODY3.csv"
                )
            )
            expected_melody3 = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_MELODY3.csv" % track
            )
            if len(melody3_glob) > 0:
                actual_melody3 = melody3_glob[0]
                self.assertEqual(
                    expected_melody3, actual_melody3
                )
            else:
                print(("[%s] Melody3 missing " % track))

    def test_ranking_names(self):
        for track in self.track_list:
            ranking_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_RANKING.txt"
                )
            )
            expected_ranking = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_RANKING.txt" % track
            )
            if len(ranking_glob) > 0:
                actual_ranking = ranking_glob[0]
                self.assertEqual(
                    expected_ranking, actual_ranking
                )
            else:
                print(("[%s] Ranking file missing " % track))

    def test_sourceid_names(self):
        for track in self.track_list:
            sourceid_glob = glob.glob(
                os.path.join(
                    ANNOT_PATH, self.annot_fmt % track, "*_SOURCEID.lab"
                )
            )
            expected_sourceid = os.path.join(
                ANNOT_PATH, self.annot_fmt % track,
                "%s_SOURCEID.lab" % track
            )
            if len(sourceid_glob) > 0:
                actual_sourceid = sourceid_glob[0]
                self.assertEqual(
                    expected_sourceid, actual_sourceid
                )
            else:
                print(("[%s] SourceID missing " % track))


@unittest.skipIf(not AUDIO_AVAILABLE, "requires audio access")
class TestMelodyAnnotations(unittest.TestCase):
    def setUp(self):
        self.track_list = TRACK_LIST

    def test_melody_annotations(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            if not mtrack.has_melody:
                continue

            mtrack.load_melody_annotations()

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
        self.track_list = TRACK_LIST

    def test_rankings(self):
        for track in self.track_list:
            mtrack = MultiTrack(track)
            rankings = list(mtrack.melody_rankings.values())
            # test that there are no duplicate rankings
            self.assertTrue(len(rankings) == len(set(rankings)))
            # test that rankings start at 1 and go up by step
            self.assertTrue(
                sorted(rankings) == list(range(1, len(rankings)+1))
            )
