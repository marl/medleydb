#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Python tools for using MedleyDB """

import logging
from os import path
from os import environ
import warnings
import yaml
import json

from .version import version as __version__

__all__ = ["__version__"]

logging.basicConfig(level=logging.CRITICAL)

if "MEDLEYDB_PATH" in environ and path.exists(environ["MEDLEYDB_PATH"]):
    MEDLEYDB_PATH = environ["MEDLEYDB_PATH"]
    AUDIO_AVAILABLE = True
elif "MEDLEYDB_PATH" not in environ:
    warnings.warn(
        "The environment variable MEDLEYDB_PATH is not set. "
        "As a result, any part of the code that requires the audio won't work. "
        "If you don't need to access the audio, disregard this warning. "
        "If you do, set the environment variable MEDLEYDB_PATH to your "
        "local copy of MedleyDB.",
        UserWarning
    )
    MEDLEYDB_PATH = ""
    AUDIO_AVAILABLE = False
else:
    MEDLEYDB_PATH = environ["MEDLEYDB_PATH"]
    warnings.warn(
        "The value set for MEDLEYDB_PATH: %s does not exist. "
        "As a result, any part of the code that requires the audio won't work. "
        "If you don't need to access the audio, disregard this warning. "
        "If you do, set the environment variable MEDLEYDB_PATH to your local "
        "copy of MedleyDB." % MEDLEYDB_PATH,
        UserWarning
    )
    AUDIO_AVAILABLE = False

# The taxonomy, tracklist, annotations and metadata are version controlled and
# stored inside the repository
ANNOT_PATH = path.join(path.dirname(__file__), 'data', 'Annotations')
METADATA_PATH = path.join(path.dirname(__file__), 'data', 'Metadata')

TRACK_LIST = []
with open(path.join(path.dirname(__file__), 'resources',
                    'tracklist_v1.txt'), 'r') as fhandle:
    for line in fhandle.readlines():
        TRACK_LIST.append(line.strip('\n'))

with open(path.join(path.dirname(__file__), 'resources',
                    'taxonomy.yaml'), 'r') as fhandle:
    INST_TAXONOMY = yaml.load(fhandle)

with open(path.join(path.dirname(__file__), 'resources',
                    'instrument_f0_type.json'), 'r') as fhandle:
    INST_F0_TYPE = json.load(fhandle)

with open(path.join(path.dirname(__file__), 'resources',
                    'mixing_coefficients.yaml'), 'r') as fhandle:
    MIXING_COEFFICIENTS = yaml.load(fhandle)

with open(path.join(path.dirname(__file__), 'resources',
                    'artist_index.json'), 'r') as fhandle:
    ARTIST_INDEX = json.load(fhandle)

# Audio is downloaded separately and is not version controlled :'(.
# This is the motivation for requesting the user to set the MEDLEYDB_PATH
if AUDIO_AVAILABLE:
    AUDIO_PATH = path.join(MEDLEYDB_PATH, 'Audio')
    if not path.exists(AUDIO_PATH):
        AUDIO_PATH = None
        warnings.warn(
            "The medleydb audio was not found at the expected path: %s "
            "This module will still function, but without the "
            "ability to access any of the audio." % AUDIO_PATH,
            UserWarning
        )
else:
    AUDIO_PATH = None

from .utils import (
    load_melody_multitracks,
    load_all_multitracks,
    load_multitracks,
    get_files_for_instrument
)

from .multitrack import (
    MultiTrack,
    Track,
    get_duration,
    read_annotation_file,
    get_valid_instrument_labels,
    is_valid_instrument
)
