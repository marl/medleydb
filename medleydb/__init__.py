#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python tools for using MedleyDB """

import logging
from os import path
from os import environ

from medleydb.version import __version__

__all__ = ["__version__", "sql"]

logging.basicConfig(level=logging.CRITICAL)

if "MEDLEYDB_PATH" not in environ:
    print """Warning: The environment variable MEDLEYDB_PATH is not set.
             As a result, any part of the code that requires the audio won't
             work. If you don't need to access the audio, disregard this warning.
             If you do, set the value of MEDLEYDB_PATH to your local path to
             the top level Audio folder for MedeleyDB."""
    MEDLEYDB_PATH = ""
else:
    MEDLEYDB_PATH = environ["MEDLEYDB_PATH"]
    assert path.exists(MEDLEYDB_PATH), """The path: %s set for MEDLEYDB_PATH does
    not exist.""" % MEDLEYDB_PATH

INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
TRACK_LIST = path.join(path.dirname(__file__), 'tracklist_v1.txt')
ANNOT_PATH = path.join(path.dirname(__file__), '../', 'Annotations')
METADATA_PATH = path.join(path.dirname(__file__), '../', 'Metadata')

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
