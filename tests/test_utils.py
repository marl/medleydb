""" Tests for utils.py """

import unittest
from medleydb import utils
from medleydb import multitrack


class TestLoadTrackList(unittest.TestCase):
    def setUp(self):
        self.track_list = utils.load_track_list()

    def test_length(self):
        self.assertEqual(len(self.track_list), 122)

    def test_inclusion(self):
        self.assertTrue('MusicDelta_SwingJazz' in set(self.track_list))

    def test_inclusion2(self):
        self.assertTrue('Grants_PunchDrunk' in set(self.track_list))


class TestLoadMelodyMultitracks(unittest.TestCase):
    def setUp(self):
        self.melody_mtracks = utils.load_melody_multitracks()
        self.first_track = next(self.melody_mtracks)

    def test_object_type(self):
        self.assertTrue(isinstance(self.first_track, multitrack.MultiTrack))

    def test_id(self):
        self.assertEqual(
            self.first_track.track_id, 'AClassicEducation_NightOwl'
        )


class TestLoadAllMultitracks(unittest.TestCase):
    def setUp(self):
        self.mtracks = utils.load_all_multitracks()
        self.first_track = next(self.mtracks)

    def test_object_type(self):
        self.assertTrue(isinstance(self.first_track, multitrack.MultiTrack))

    def test_id(self):
        self.assertEqual(
            self.first_track.track_id, 'AClassicEducation_NightOwl'
        )


class TestLoadMultitracks(unittest.TestCase):
    def test_single_track(self):
        res = utils.load_multitracks(['MusicDelta_SwingJazz'])
        track = next(res)
        self.assertEqual(track.track_id, 'MusicDelta_SwingJazz')

    def test_two_tracks(self):
        res = utils.load_multitracks(['AmarLal_Rest', 'AmarLal_SpringDay1'])
        res_list = list(res)
        self.assertEqual(len(res_list), 2)

    def test_bad_id(self):
        res = utils.load_multitracks(
                ['MusicDelta_Reggae', 'RickAstley_NeverGonnaGiveYouUp']
        )
        with self.assertRaises(IOError):
            list(res)


class TestGetFilesForInstrument(unittest.TestCase):
    def setUp(self):
        self.files = ['AimeeNorwich_Flying', 'MusicDelta_Reggae']
        self.mtrack_list = utils.load_multitracks(self.files)

    def test_subset(self):
        trombone_files = utils.get_files_for_instrument(
            'trombone', self.mtrack_list
        )
        self.assertEqual(len(list(trombone_files)), 2)

    def test_subset2(self):
        male_singer_files = utils.get_files_for_instrument(
            'male singer', self.mtrack_list
        )
        self.assertEqual(len(list(male_singer_files)), 1)

    def test_invalid_inst(self):
        with self.assertRaises(ValueError):
            list(utils.get_files_for_instrument('mayonnaise'))

