import logging
import yaml
from os import path

logging.basicConfig(level=logging.CRITICAL)

f_in = open(path.join(path.dirname(__file__), 'config.yaml'))
config_vars = yaml.load(f_in)
f_in.close()

MEDLEYDB_DIR = config_vars['MEDLEYDB_DIR']

INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
AUDIO_DIR = path.join(MEDLEYDB_DIR, 'Audio')
ANNOTATION_DIR = path.join(MEDLEYDB_DIR, 'Annotations')
MELODY_DIR = path.join(ANNOTATION_DIR, 'Melody_Annotations')
PITCH_DIR = path.join(ANNOTATION_DIR, 'Pitch_Annotations')

from . import dataset_utils
from . import multitrack