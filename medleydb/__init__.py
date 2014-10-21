#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python tools for using MedleyDB """

import logging
from os import path
from os import environ

logging.basicConfig(level=logging.CRITICAL)

assert "MEDLEYDB_PATH" in environ, """The environment variable MEDLEYDB_PATH 
is not set. Set the value of MEDLEYDB_DIR to your local path to MedeleyDB."""

MEDLEYDB_DIR = environ["MEDLEYDB_PATH"]

assert path.exists(MEDLEYDB_DIR), """The path: %s set for MEDLEYDB_PATH does 
not exist.""" % MEDLEYDB_DIR

INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
AUDIO_DIR = path.join(MEDLEYDB_DIR, 'Audio')
ANNOTATION_DIR = path.join(MEDLEYDB_DIR, 'Annotations')
MELODY_DIR = path.join(ANNOTATION_DIR, 'Melody_Annotations')
PITCH_DIR = path.join(ANNOTATION_DIR, 'Pitch_Annotations')

from .utils import *
from .multitrack import *
