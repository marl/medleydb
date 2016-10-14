""" Tests for medleydb.mix
"""
import unittest
import os

from medleydb import multitrack
from medleydb import mix
from medleydb import AUDIO_PATH


OUTPUT_PATH = 'test_out.wav'


def clean_output():
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)


class TestMixMultitrack(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('LizNelson_Rainfall')

    def test_defaults(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_less_stems(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH, stem_indices=[2, 4]
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_alt_weights(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH, alternate_weights={2: 2.0, 4: 0.5}
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_alt_files(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH,
            alternate_files={1: self.mtrack.mix_path}
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()


    def test_additional_files(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH,
            additional_files=[(self.mtrack.mix_path, 2.1)]
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_one_stem_mix(self):
        clean_output()
        mix.mix_multitrack(
            self.mtrack, OUTPUT_PATH, stem_indices=[2]
        )
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()


class TestBuildMixArgs(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('LizNelson_Rainfall')

    def test_defaults(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, None, None, None, None
        )
        expected_filepaths = [
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['01', '02', '03', '04', '05']
        ]
        expected_weights = [
            0.6354871509502455,
            0.12610504621272442,
            0.0624147327727016,
            0.8433924607944484,
            0.29222231756693756
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)

    def test_less_stems(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, [2, 4], None, None, None
        )
        expected_filepaths = [
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['02', '04']
        ]
        expected_weights = [
            0.12610504621272442,
            0.8433924607944484,
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)

    def test_alt_weights(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, None, {2: 2.0, 4: 0.5}, None, None
        )
        expected_filepaths = [
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['01', '02', '03', '04', '05']
        ]
        expected_weights = [
            0.6354871509502455,
            2.0,
            0.0624147327727016,
            0.5,
            0.29222231756693756
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)

    def test_alt_files(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, None, None, {1: self.mtrack.mix_path}, None
        )
        expected_filepaths = [
            os.path.join(
                AUDIO_PATH, 'LizNelson_Rainfall', 'LizNelson_Rainfall_MIX.wav'
            )
        ]
        expected_filepaths.extend([
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['02', '03', '04', '05']
        ])
        expected_weights = [
            0.6354871509502455,
            0.12610504621272442,
            0.0624147327727016,
            0.8433924607944484,
            0.29222231756693756
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)


    def test_additional_files(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, None, None, None, [(self.mtrack.mix_path, 2.1)]
        )
        expected_filepaths = [
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['01', '02', '03', '04', '05']
        ]
        expected_filepaths.append(self.mtrack.mix_path)
        expected_weights = [
            0.6354871509502455,
            0.12610504621272442,
            0.0624147327727016,
            0.8433924607944484,
            0.29222231756693756,
            2.1
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)

    def test_one_stem_mix(self):
        actual_filepaths, actual_weights = mix._build_mix_args(
            self.mtrack, [2], None, None, None
        )
        expected_filepaths = [
            os.path.join(AUDIO_PATH, 'LizNelson_Rainfall',
                         'LizNelson_Rainfall_STEMS',
                         'LizNelson_Rainfall_STEM_{}.wav'.format(i))
            for i in ['02']
        ]
        expected_weights = [
            0.12610504621272442
        ]
        self.assertEqual(expected_filepaths, actual_filepaths)
        self.assertEqual(expected_weights, actual_weights)


class TestMixMelodyStems(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('Phoenix_ScotchMorris')

    def test_defaults(self):
        clean_output()
        actual_melody, actual_stem = mix.mix_melody_stems(
            self.mtrack, OUTPUT_PATH
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_melody)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_max_melody_stems1(self):
        clean_output()
        actual_melody, actual_stem = mix.mix_melody_stems(
            self.mtrack, OUTPUT_PATH, max_melody_stems=1
        )
        expected_melody = [2]
        expected_stem = [2]
        self.assertEqual(expected_melody, actual_melody)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_max_melody_stems2(self):
        clean_output()
        actual_melody, actual_stem = mix.mix_melody_stems(
            self.mtrack, OUTPUT_PATH, max_melody_stems=3
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_melody)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_include_percussion(self):
        clean_output()
        actual_melody, actual_stem = mix.mix_melody_stems(
            self.mtrack, OUTPUT_PATH, include_percussion=True
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_melody)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_require_mono(self):
        clean_output()
        actual_melody, actual_stem = mix.mix_melody_stems(
            self.mtrack, OUTPUT_PATH, require_mono=True
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_melody)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()


class TestMixMonoStems(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('Phoenix_ScotchMorris')

    def test_defaults(self):
        clean_output()
        actual_mono, actual_stem = mix.mix_mono_stems(
            self.mtrack, OUTPUT_PATH
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_mono)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()

    def test_include_percussion(self):
        clean_output()
        actual_mono, actual_stem = mix.mix_mono_stems(
            self.mtrack, OUTPUT_PATH, include_percussion=True
        )
        expected_melody = [2, 3]
        expected_stem = [2, 3]
        self.assertEqual(expected_melody, actual_mono)
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()


class TestMixNoVocals(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('LizNelson_Rainfall')

    def test_defaults(self):
        clean_output()
        actual_stem = mix.mix_no_vocals(
            self.mtrack, OUTPUT_PATH
        )
        expected_stem = [4, 5]
        self.assertEqual(expected_stem, actual_stem)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()


class TestRemixVocals(unittest.TestCase):
    def setUp(self):
        self.mtrack = multitrack.MultiTrack('LizNelson_Rainfall')

    def test_defaults(self):
        clean_output()
        alt_weights = mix.remix_vocals(
            self.mtrack, OUTPUT_PATH, 2.0
        )
        expected_weights = {
            1: 1.270974301900491,
            2: 0.25221009242544884,
            3: 0.1248294655454032
        }
        self.assertEqual(expected_weights, alt_weights)
        self.assertTrue(os.path.exists(OUTPUT_PATH))
        clean_output()
