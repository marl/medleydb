"""Tests for generate_melody_annotations script"""
import unittest
import os
import numpy as np
from medleydb import MultiTrack
from medleydb.annotate import generate_melody_annotations as G

HOP = 256.0
FS = 44100.0


def array_almost_equal(array1, array2, tolerance=1e-7):
    diff = np.abs(array1 - array2)
    num_not_equal = diff > tolerance
    print("number of unequal elements: %s" % np.sum(num_not_equal))
    return np.sum(num_not_equal) == 0


class TestGetTimeStamps(unittest.TestCase):

    def test_get_time_stamps(self):
        dur = 0.02902494331  # seconds
        actual = G.get_time_stamps(dur)
        expected = np.array([0.0, HOP/FS, 2.0*HOP/FS, 3.0*HOP/FS, 4.0*HOP/FS])
        self.assertTrue(array_almost_equal(actual, expected))


class TestMakeBlakMelodySequence(unittest.TestCase):

    def test_get_blank_melody_sequence(self):
        dur = 0.02902494331  # seconds
        actual = G.make_blank_melody_sequence(dur)
        times = [0.0, HOP/FS, 2.0*HOP/FS, 3.0*HOP/FS, 4.0*HOP/FS]
        expected = np.array([
            [times[0], 0.0],
            [times[1], 0.0],
            [times[2], 0.0],
            [times[3], 0.0],
            [times[4], 0.0]
        ])
        self.assertTrue(array_almost_equal(actual, expected))

class TestSecToIdx(unittest.TestCase):

    def test_defaults1(self):
        actual = G.sec_to_idx(0.0)
        expected = 0
        self.assertEqual(actual, expected)

    def test_defaults2(self):
        actual = G.sec_to_idx(2.0*256.0/44100.0)
        expected = 2
        self.assertEqual(actual, expected)

    def test_fs1(self):
        actual = G.sec_to_idx(0.0, fs=1000)
        expected = 0
        self.assertEqual(actual, expected)

    def test_fs2(self):
        actual = G.sec_to_idx(2.0*256.0/1000.0, fs=1000)
        expected = 2
        self.assertEqual(actual, expected)

    def test_hop1(self):
        actual = G.sec_to_idx(0.0, hop=2)
        expected = 0
        self.assertEqual(actual, expected)

    def test_hop2(self):
        actual = G.sec_to_idx(4.0*2.0/44100.0, hop=2)
        expected = 4
        self.assertEqual(actual, expected)

class TestAddSequenceToMelody(unittest.TestCase):

    def setUp(self):
        self.times = [0.0, HOP/FS, 2.0*HOP/FS, 3.0*HOP/FS, 4.0*HOP/FS]
        self.dur = 0.02902494331  # seconds

    def test_add_sequence_to_melody1(self):

        f0_sequence = [
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        actual = G.add_sequence_to_melody(self.dur, f0_sequence, melody_sequence)
        expected = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

    def test_add_sequence_to_melody2(self):

        f0_sequence = [
            [self.times[0], 3.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        actual = G.add_sequence_to_melody(self.dur, f0_sequence, melody_sequence)
        expected = np.array([
            [self.times[0], 3.0],
            [self.times[1], 0.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
            [self.times[4], 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

    def test_add_sequence_to_melody3(self):

        f0_sequence = [
            [self.times[0], 3.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        actual = G.add_sequence_to_melody(
            self.dur, f0_sequence, melody_sequence, start_t=0.0059
        )
        expected = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
            [self.times[4], 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

    def test_add_sequence_to_melody4(self):

        f0_sequence = [
            [self.times[0], 3.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        actual = G.add_sequence_to_melody(
            self.dur, f0_sequence, melody_sequence, end_t=0.0059
        )
        expected = np.array([
            [self.times[0], 3.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

    def test_add_sequence_to_melody4(self):

        f0_sequence = [
            [self.times[0], 3.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 0.0],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        actual = G.add_sequence_to_melody(
            self.dur, f0_sequence, melody_sequence, start_t=0.0059, end_t=0.017
        )
        expected = np.array([
            [self.times[0], 0.0],
            [self.times[1], 0.0],
            [self.times[2], 1.7],
            [self.times[3], 0.0],
            [self.times[4], 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

    def test_add_sequence_to_melody4(self):

        f0_sequence = [
            [self.times[0], 3.0],
            [self.times[2], 1.7],
            [self.times[3], 100.0],
        ]
        melody_sequence = np.array([
            [self.times[0], 0.0, 0.0],
            [self.times[1], 2.3, 0.0],
            [self.times[2], 0.0, 0.0],
            [self.times[3], 0.0, 0.0],
            [self.times[4], 8.1, 0.0]
        ])
        actual = G.add_sequence_to_melody(
            self.dur, f0_sequence, melody_sequence, dim=2
        )
        expected = np.array([
            [self.times[0], 0.0, 3.0],
            [self.times[1], 2.3, 0.0],
            [self.times[2], 0.0, 1.7],
            [self.times[3], 0.0, 100.0],
            [self.times[4], 8.1, 0.0]
        ])
        print(actual)
        print(expected)
        self.assertTrue(array_almost_equal(actual, expected))

class TestCreateMelodyAnnotations(unittest.TestCase):

    def setUp(self):
        self.mtrack = MultiTrack("MusicDelta_Beethoven")
        self.mtrack.duration = 27.371
        self.mtrack.load_melody_annotations()
        self.mtrack_nomel = MultiTrack("TablaBreakbeatScience_Animoog")

    def test_melody1(self):
        actual = G.create_melody1_annotation(self.mtrack)
        expected = self.mtrack.melody1_annotation
        self.assertTrue(array_almost_equal(actual, expected))

    def test_melody2(self):
        actual = G.create_melody2_annotation(self.mtrack)
        expected = self.mtrack.melody2_annotation
        self.assertTrue(array_almost_equal(actual, expected))

    def test_melody3(self):
        actual = G.create_melody3_annotation(self.mtrack)
        expected = self.mtrack.melody3_annotation
        self.assertTrue(array_almost_equal(actual, expected))

    def test_melody1none(self):
        actual = G.create_melody1_annotation(self.mtrack_nomel)
        expected = None
        self.assertEqual(expected, actual)

    def test_melody2none(self):
        actual = G.create_melody2_annotation(self.mtrack_nomel)
        expected = None
        self.assertEqual(expected, actual)

    def test_melody3none(self):
        actual = G.create_melody3_annotation(self.mtrack_nomel)
        expected = None
        self.assertEqual(expected, actual)


class TestWriteMelodiesToCsv(unittest.TestCase):

    def setUp(self):
        self.mtrack = MultiTrack("TablaBreakbeatScience_Animoog")
        self.melody1 = np.array([
            [0.0, 0.0],
            [1.0, 440.0],
            [2.0, 450.0],
            [3.0, 460.0],
            [4.0, 0.0]
        ])
        self.melody2 = np.array([
            [0.0, 430.0],
            [1.0, 440.0],
            [2.0, 450.0],
            [3.0, 460.0],
            [4.0, 0.0]
        ])
        self.melody3 = np.array([
            [0.0, 0.0, 120.0],
            [1.0, 440.0, 0.0],
            [2.0, 450.0, 0.0],
            [3.0, 460.0, 234.1],
            [4.0, 0.0, 123.1]
        ])

    def test_melody1(self):
        expected_output_path = os.path.join(
            self.mtrack.annotation_dir,
            'TablaBreakbeatScience_Animoog_MELODY1.csv'
        )
        G.write_melodies_to_csv(self.mtrack, self.melody1, None, None)
        self.assertTrue(os.path.exists(expected_output_path))
        os.remove(expected_output_path)

    def test_melody2(self):
        expected_output_path = os.path.join(
            self.mtrack.annotation_dir,
            'TablaBreakbeatScience_Animoog_MELODY2.csv'
        )
        G.write_melodies_to_csv(self.mtrack, None, self.melody2, None)
        self.assertTrue(os.path.exists(expected_output_path))
        os.remove(expected_output_path)

    def test_melody3(self):
        expected_output_path = os.path.join(
            self.mtrack.annotation_dir,
            'TablaBreakbeatScience_Animoog_MELODY3.csv'
        )
        G.write_melodies_to_csv(self.mtrack, None, None, self.melody3)
        self.assertTrue(os.path.exists(expected_output_path))
        os.remove(expected_output_path)

