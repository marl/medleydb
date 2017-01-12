"""Tests for medleydb.download
"""
import os
import unittest
from pydrive.auth import AuthenticationError

from medleydb import download
from medleydb import MultiTrack


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class TestAuthorizeGoogleDrive(unittest.TestCase):
    def test_failed_authorize(self):
        with self.assertRaises(AuthenticationError):
            download.authorize_google_drive()


class TestPurgeDownloadedFiles(unittest.TestCase):
    def test_purge(self):
        tempfile1 = 'tempfile1.wav'
        tempfile2 = 'tempfile2.wav'
        touch(tempfile1)
        touch(tempfile2)
        download.DOWNLOADED_FILEPATHS = [tempfile1, tempfile2]

        self.assertTrue(os.path.exists(tempfile1))
        self.assertTrue(os.path.exists(tempfile2))

        download.purge_downloaded_files()

        self.assertFalse(os.path.exists(tempfile1))
        self.assertFalse(os.path.exists(tempfile2))


class TestCheckBaseDirWriteable(unittest.TestCase):
    def test_writeable(self):
        actual = download.check_basedir_writeable()
        expected = True
        self.assertEqual(expected, actual)
        self.assertTrue(download.BASEDIR_WRITEABLE)


class TestMakeMtrackBasedir(unittest.TestCase):
    def test_make_mtrack_basedir(self):
        mtrack = MultiTrack('MusicDelta_Rock')

        self.assertFalse(os.path.exists(mtrack.audio_path))
        self.assertFalse(os.path.exists(mtrack._stem_dir_path))
        self.assertFalse(os.path.exists(mtrack._raw_dir_path))

        download.make_mtrack_basedir(mtrack)

        self.assertTrue(os.path.exists(mtrack.audio_path))
        self.assertTrue(os.path.exists(mtrack._stem_dir_path))
        self.assertTrue(os.path.exists(mtrack._raw_dir_path))


class TestDownloadMix(unittest.TestCase):
    def test_existing(self):
        mtrack = MultiTrack('LizNelson_Rainfall')
        download.download_mix(mtrack)
        self.assertTrue(os.path.exists(mtrack.mix_path))

    def test_not_in_tracklist(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        mtrack.dataset_version = ''
        with self.assertRaises(IOError):
            download.download_mix(mtrack)

    def test_failed_download(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        with self.assertRaises(AuthenticationError):
            download.download_mix(mtrack)


class TestDownloadStem(unittest.TestCase):
    def test_existing(self):
        mtrack = MultiTrack('LizNelson_Rainfall')
        download.download_stem(mtrack, 1)
        self.assertTrue(os.path.exists(mtrack.stems[1].audio_path))

    def test_not_in_tracklist(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        mtrack.dataset_version = ''
        with self.assertRaises(IOError):
            download.download_stem(mtrack, 1)

    def test_failed_download(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        with self.assertRaises(AuthenticationError):
            download.download_stem(mtrack, 1)


class TestDownloadRaw(unittest.TestCase):
    def test_existing(self):
        mtrack = MultiTrack('LizNelson_Rainfall')
        download.download_raw(mtrack, 1, 1)
        self.assertTrue(os.path.exists(mtrack.raw_audio[1][1].audio_path))

    def test_not_in_tracklist(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        mtrack.dataset_version = ''
        with self.assertRaises(IOError):
            download.download_raw(mtrack, 1, 1)

    def test_failed_download(self):
        mtrack = MultiTrack('MusicDelta_Beethoven')
        with self.assertRaises(AuthenticationError):
            download.download_raw(mtrack, 1, 1)


class TestGetNamedChild(unittest.TestCase):
    def test_auth_failure(self):
        with self.assertRaises(AuthenticationError):
            download.get_named_child('asdf', 'asdf')


class TestGetFilesInFolder(unittest.TestCase):
    def test_auth_failure(self):
        with self.assertRaises(AuthenticationError):
            download.get_files_in_folder('asdf')


class TestDownloadFile(unittest.TestCase):
    def test_auth_failure(self):
        with self.assertRaises(AuthenticationError):
            download.download_file('asdf', 'asdf')

