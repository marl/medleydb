#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python tools for using MedleyDB """

import logging
from os import path
from os import environ

logging.basicConfig(level=logging.CRITICAL)

assert "MEDLEYDB_PATH" in environ, """The environment variable MEDLEYDB_PATH
is not set. Set the value of MEDLEYDB_PATH to your local path to MedeleyDB."""

MEDLEYDB_PATH = environ["MEDLEYDB_PATH"]

assert path.exists(MEDLEYDB_PATH), """The path: %s set for MEDLEYDB_PATH does
not exist.""" % MEDLEYDB_PATH

INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
AUDIO_DIR = path.join(MEDLEYDB_PATH, 'Audio')
ANNOTATION_DIR = path.join(MEDLEYDB_PATH, 'Annotations')
MELODY_DIR = path.join(ANNOTATION_DIR, 'Melody_Annotations')
PITCH_DIR = path.join(ANNOTATION_DIR, 'Pitch_Annotations')
RANKINGS_DIR = path.join(ANNOTATION_DIR, 'Stem_Rankings')

from .utils import (
    load_melody_multitracks,
    load_all_multitracks,
    load_multitracks,
    get_files_for_instrument,
    preview_audio
)

from .multitrack import (
    MultiTrack,
    Track,
    get_duration,
    read_annotation_file,
    get_valid_instrument_labels,
    is_valid_instrument
)
