"""Tests for generate_melody_annotations script"""
from __future__ import print_function

import unittest
from medleydb.annotate import pyin_pitch as G


class TestCheckBinary(unittest.TestCase):
    def test_binary_unavail(self):
        actual = G._check_binary()
        expected = False
        self.assertEqual(expected, actual)


class TestRunPyin(unittest.TestCase):
    def test_env_error(self):
        with self.assertRaises(EnvironmentError):
            G.pyin_pitch("asdf", "asdf")
