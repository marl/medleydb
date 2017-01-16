from __future__ import print_function

import unittest
import numpy as np
import os
from medleydb import MultiTrack
from medleydb.annotate import activation_conf as A


def array_almost_equal(array1, array2, tolerance=1e-7):
    diff = np.abs(array1 - array2)
    num_not_equal = diff > tolerance
    print("number of unequal elements: %s" % np.sum(num_not_equal))
    return np.sum(num_not_equal) == 0


class TestComputeActivationConfidence(unittest.TestCase):

    def test_defaults(self):
        mtrack = MultiTrack('LizNelson_Rainfall')
        C, actual_index = A.compute_activation_confidence(mtrack)
        actual_shape = C.shape
        expected_shape = (6135, 6)
        self.assertEqual(expected_shape, actual_shape)
        
        expected_index = [1, 2, 3, 4, 5]
        self.assertEqual(expected_index, actual_index)


class TestTrackEnergy(unittest.TestCase):

    def test_compute_energy(self):
        wave = np.ones((20, ))
        win_len = 10
        win = np.ones((10, ))
        actual = A.track_energy(wave, win_len, win)
        expected = np.array([0.5, 1., 1., 1., 0.5])
        self.assertTrue(np.allclose(expected, actual))

class TestHwr(unittest.TestCase):

    def test_neg_pos(self):
        x = np.array([-0.5, 0, 0.5])
        expected = np.array([0, 0, 0.5])
        actual = A.hwr(x)

    def test_pos(self):
        x = np.array([7, 0, 0.5])
        expected = np.array([7, 0, 0.5])
        actual = A.hwr(x)


class TestWriteActivationsToCsv(unittest.TestCase):

    def test_default(self):
        activations = np.array([
            [0.0, 1.0, 1.0, 0.4],
            [0.5, 0.9, 0.9, 0.7],
            [1.0, 0.8, 0.8, 0.8]
        ])
        mtrack = MultiTrack('Phoenix_ScotchMorris')
        stem_idx_list = [1, 2, 3]
        A.write_activations_to_csv(mtrack, activations, stem_idx_list)
        self.assertTrue(os.path.exists(mtrack.activation_conf_fpath))

        os.remove(mtrack.activation_conf_fpath)


