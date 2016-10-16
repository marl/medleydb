import unittest
import glob
import yaml
import os

from medleydb import METADATA_PATH


class TestFileNames(unittest.TestCase):

    def setUp(self):
        self.expected_keys = sorted([
            'album',
            'artist',
            'composer',
            'excerpt',
            'genre',
            'has_bleed',
            'instrumental',
            'mix_filename',
            'origin',
            'producer',
            'raw_dir',
            'stem_dir',
            'stems',
            'title',
            'version',
            'website'
        ])
        self.expected_version = 1.2

    def test_metadata(self):
        for fpath in glob.glob(os.path.join(METADATA_PATH, '*.yaml')):
            with open(fpath, 'r') as f_in:
                metadata = yaml.load(f_in)
            actual_keys = sorted(metadata.keys())
            self.assertEqual(self.expected_keys, actual_keys)
            self.assertEqual(self.expected_version, metadata['version'])
