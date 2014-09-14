import logging
import yaml
from os import path

logging.basicConfig(level=logging.CRITICAL)

_CONFIG_FILE = open(path.join(path.dirname(__file__), 'config.yaml'))
_CONFIG_VARS = yaml.load(_CONFIG_FILE)
_CONFIG_FILE.close()

MEDLEYDB_DIR = _CONFIG_VARS['MEDLEYDB_DIR']
assert MEDLEYDB_DIR, """No local directory set in config.yaml 
Set the value of MEDLEYDB_DIR in medleydb/multitrack/config.yaml 
to your local path to the MedleyDB dataset."""

assert path.exists(MEDLEYDB_DIR), """The absolute path:
%s
set in config.yaml does not exist.""" % MEDLEYDB_DIR

INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
AUDIO_DIR = path.join(MEDLEYDB_DIR, 'Audio')
ANNOTATION_DIR = path.join(MEDLEYDB_DIR, 'Annotations')
MELODY_DIR = path.join(ANNOTATION_DIR, 'Melody_Annotations')
PITCH_DIR = path.join(ANNOTATION_DIR, 'Pitch_Annotations')

from . import dataset_utils
from . import multitrack
