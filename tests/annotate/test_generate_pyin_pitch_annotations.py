"""Tests for generate_melody_annotations script"""
from __future__ import print_function

import unittest
import os
import numpy as np
from medleydb import MultiTrack
from medleydb.annotate import generate_pyin_pitch_annotations as G


def array_almost_equal(array1, array2, tolerance=1e-7):
    diff = np.abs(array1 - array2)
    num_not_equal = diff > tolerance
    print("number of unequal elements: %s" % np.sum(num_not_equal))
    return np.sum(num_not_equal) == 0


def TestCheckBinary(unittest.TestCase):
    def test_binary_unavail(self):
        actual = G._check_binary()
        expected = False
        self.assertEqual(expected, actual)


def TestRunPyin(unittest.TestCase):
    def test_env_error(self):
        with self.assertRaises(EnvironmentError):
            G.run_pyin("asdf", "asdf")
