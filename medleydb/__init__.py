#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python tools for using MedleyDB """

import logging
from os import path
from os import environ

from medleydb.version import __version__

__all__ = ["__version__", "sql"]

logging.basicConfig(level=logging.CRITICAL)

if "MEDLEYDB_PATH" in environ and path.exists(environ["MEDLEYDB_PATH"]):
    AUDIO_AVAILABLE = True
elif "MEDLEYDB_PATH" not in environ:
    print """Warning: The environment variable MEDLEYDB_PATH is not set.
             As a result, any part of the code that requires the audio won't
             work. If you don't need to access the audio, disregard this warning.
             If you do, set the value of MEDLEYDB_PATH to your local path to
             MedeleyDB."""
    MEDLEYDB_PATH = ""
    AUDIO_AVAILABLE = False
else:
    MEDLEYDB_PATH = environ["MEDLEYDB_PATH"]
    print """Warning: The value set for MEDLEYDB_PATH: %s does not exist.
             As a result, any part of the code that requires the audio won't
             work. If you don't need to access the audio, disregard this warning.
             If you do, set the value of MEDLEYDB_PATH to your local path to
             MedeleyDB.""" % MEDLEYDB_PATH
    AUDIO_AVAILABLE = False

# The taxonomy, tracklist, annotations and metadata are version controlled and
# stored inside the repository
INST_TAXONOMY = path.join(path.dirname(__file__), 'taxonomy.yaml')
TRACK_LIST = path.join(path.dirname(__file__), 'tracklist_v1.txt')
ANNOT_PATH = path.join(path.dirname(__file__), '../', 'Annotations')
METADATA_PATH = path.join(path.dirname(__file__), '../', 'Metadata')

# Audio is downloaded separately and is not version controlled :'(.
# This is the motivation for requiring the user to set the MEDLEYDB_PATH
if AUDIO_AVAILABLE:
    AUDIO_PATH = path.join(MEDLEYDB_PATH, 'Audio')
    if not path.exists(AUDIO_PATH):
        AUDIO_PATH = None
        print """Warning: The medleydb audio was not found at the expected path.
                 The module will still function, but without the
                 ability to access any of the audio."""
        print """Expected MedleyDB audio path: %s""" % AUDIO_PATH
else:
    AUDIO_PATH = None

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
