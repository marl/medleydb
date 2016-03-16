#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class definitions for MedleyDB multitracks."""

from __future__ import print_function

import os
import yaml
import wave
import csv
from . import INST_TAXONOMY
from . import INST_F0_TYPE
from . import MIXING_COEFFICIENTS
from . import ANNOT_PATH
from . import METADATA_PATH
from . import AUDIO_PATH

_YESNO = dict(yes=True, no=False)
_TRACKID_FMT = "%s_%s"
_METADATA_FMT = "%s_METADATA.yaml"
_STEMDIR_FMT = "%s_STEMS"
_RAWDIR_FMT = "%s_RAW"
_MIX_FMT = "%s_MIX.wav"
_STEM_FMT = "%s_STEM_%%s.wav"
_RAW_FMT = "%s_RAW_%%s_%%s.wav"

_AUDIODIR_FMT = "%s"

_ANNOTDIR_FMT = "%s_ANNOTATIONS"
_ACTIVCONF_FMT = "%s_ACTIVATION_CONF.lab"
_INTERVAL_FMT = "%s_INTERVALS.txt"
_MELODY1_FMT = "%s_MELODY1.csv"
_MELODY2_FMT = "%s_MELODY2.csv"
_MELODY3_FMT = "%s_MELODY3.csv"
_RANKING_FMT = "%s_RANKING.txt"
_SOURCEID_FMT = "%s_SOURCEID.lab"
_PITCHDIR_FMT = "%s_PITCH"
_PITCH_FMT = "%s.csv"


class MultiTrack(object):
    """MultiTrack Class definition.

    This class loads all available metadata, annotations, and filepaths for a
    given multitrack directory.

    Examples:
        >>> mtrack = Multitrack('LizNelson_Rainfall')
        >>> another_mtrack = Multitrack('ArtistName_TrackTitle')

    Attributes:
        artist (str): Artist.
        duration (float): Track duration, in seconds.
        genre (str): Track genre label.
        has_bleed (bool): True if track has stems with bleed.
        is_excerpt (bool): True if track is an excerpt.
        is_instrumental (bool): True if track is instrumental.
        melody1_annotation (list): time, f0 lists from melody 1 annotation.
        melody2_annotation (list): time, f0 lists from melody 2 annotation.
        melody3_annotation (list): time, f0 lists from melody 3 annotation.
        melody_rankings (list): melody stem predominance rankings.
            Keys: stem_idx (int), values: ranking (int)
        mix_path (str): Full path to MIX file.
        mtrack_path (str): Full path to folder containing multitrack.
        origin (str): Track origin.
        raw_audio (list of Track objects): List of raw audio tracks.
        raw_instruments (list of strings): List of raw track instrument labels.
        stem_instruments (list of strings): List of stem instrument labels.
        stem_activations (list): List of stem activation confidence annotations
        stems (list of Track objects): List of stems.
        title (str): Track title.
        track_id (str): Unique track id in the form "ArtistName_TrackTitle".
    """

    def __init__(self, track_id):
        """MultiTrack object __init__ method.

        Args:
            track_id (str): Track id in format 'Artist_Title'.

        """

        # Artist, Title & Track Directory #
        if AUDIO_PATH:
            self.audio_path = os.path.join(
                AUDIO_PATH, _AUDIODIR_FMT % track_id
            )
        self.artist = track_id.split('_')[0]
        self.title = track_id.split('_')[1]
        self.track_id = track_id

        # Filenames and Filepaths #
        self._meta_path = os.path.join(
            METADATA_PATH, _METADATA_FMT % self.track_id
        )

        # break if metadata file cannot be found
        if not os.path.exists(self._meta_path):
            raise IOError("Cannot find metadata for %s" % self.track_id)

        self.annotation_dir = os.path.join(
            ANNOT_PATH, _ANNOTDIR_FMT % self.track_id
        )
        self._pitch_path = os.path.join(
            self.annotation_dir, _PITCHDIR_FMT % self.track_id
        )

        if AUDIO_PATH:
            self._stem_dir_path = os.path.join(
                self.audio_path, _STEMDIR_FMT % self.track_id
            )
            self._raw_dir_path = os.path.join(
                self.audio_path, _RAWDIR_FMT % self.track_id
            )
            self.mix_path = os.path.join(
                self.audio_path, _MIX_FMT % self.track_id
            )
        else:
            self._stem_dir_path = None
            self._raw_dir_path = None
            self.mix_path = None

        # Stem & Raw File Formats #
        self._stem_fmt = _STEM_FMT % self.track_id
        self._raw_fmt = _RAW_FMT % self.track_id

        # Yaml Dictionary of Metadata #
        self._metadata = self._load_metadata()

        self._melody_rankings_fpath = os.path.join(
            self.annotation_dir, _RANKING_FMT % self.track_id
        )
        self.melody_rankings = self._get_melody_rankings()

        self.mixing_coefficients = MIXING_COEFFICIENTS[self.track_id]

        # Stem & Raw Dictionaries. Lists of filepaths. #
        self.stems, self.raw_audio = self._parse_metadata()

        # Lists of Instrument Labels #
        self.stem_instruments = sorted(
            [s.instrument for s in self.stems.values()]
        )
        self.raw_instruments = sorted(
            [r.instrument for r in get_dict_leaves(self.raw_audio)]
        )

        # Basic Track Information #
        if self.mix_path is not None and os.path.exists(self.mix_path):
            self.duration = get_duration(self.mix_path)
        else:
            print(("Warning: Audio missing for %s." % self.track_id))
            self.duration = None

        self.is_excerpt = _YESNO[self._metadata['excerpt']]
        self.has_bleed = _YESNO[self._metadata['has_bleed']]
        self.is_instrumental = _YESNO[self._metadata['instrumental']]
        self.origin = self._metadata['origin']
        self.genre = self._metadata['genre']

        mel1_path = os.path.join(self.annotation_dir,
                                 _MELODY1_FMT % self.track_id)
        self.has_melody = os.path.exists(mel1_path)

        self.melody1_annotation = None
        self.melody2_annotation = None
        self.melody3_annotation = None

        self.predominant_stem = self._get_predominant_stem()
        self.stem_activations, self.stem_activations_idx = \
            self._get_activation_annotations()

    def _load_metadata(self):
        """Load the metadata file.
        """
        with open(self._meta_path, 'r') as f_in:
            metadata = yaml.load(f_in)
        return metadata

    def _parse_metadata(self):
        """Parse metadata dictionary.
        """
        stems = dict()
        raw_audio = dict()
        stem_dict = self._metadata['stems']

        for k in stem_dict:
            stem_idx = int(k[1:])

            instrument = stem_dict[k]['instrument']
            component = stem_dict[k]['component']

            if stem_idx in self.melody_rankings:
                ranking = self.melody_rankings[stem_idx]
            else:
                ranking = None

            if AUDIO_PATH:
                file_name = stem_dict[k]['filename']
                file_path = os.path.join(self._stem_dir_path, file_name)
            else:
                file_path = None

            pitch_path = os.path.join(
                self._pitch_path,
                "%s_STEM_%s.csv" % (self.track_id, k[1:])
            )

            track = Track(instrument=instrument, file_path=file_path,
                          component=component, stem_idx=stem_idx,
                          ranking=ranking, mix_path=self.mix_path,
                          pitch_path=pitch_path,
                          mix_coeff=self.mixing_coefficients[stem_idx])

            stems[stem_idx] = track
            raw_dict = stem_dict[k]['raw']

            for j in raw_dict:
                raw_idx = int(j[1:])
                instrument = raw_dict[j]['instrument']

                if AUDIO_PATH:
                    file_name = raw_dict[j]['filename']
                    file_path = os.path.join(self._raw_dir_path, file_name)
                else:
                    file_path = None

                track = Track(instrument=instrument, file_path=file_path,
                              stem_idx=stem_idx, raw_idx=raw_idx,
                              mix_path=self.mix_path, ranking=ranking)
                if stem_idx not in raw_audio:
                    raw_audio[stem_idx] = {}

                raw_audio[stem_idx][raw_idx] = track

        return stems, raw_audio

    def _get_melody_rankings(self):
        """Get rankings from the melody rankings annotation file.
        """
        melody_rankings = {}
        if os.path.exists(self._melody_rankings_fpath):
            with open(self._melody_rankings_fpath) as f_handle:
                linereader = csv.reader(f_handle)
                for line in linereader:
                    stem_idx = int(line[0].split('_')[-1].split('.')[0])
                    ranking = int(line[1])
                    melody_rankings[stem_idx] = ranking
        return melody_rankings

    def _get_predominant_stem(self):
        """Get predominant stem if files exists.
        """

        if len(self.melody_rankings) > 0:
            predominant_idx = [
                k for k, v in self.melody_rankings.items() if v == 1
            ]
            if len(predominant_idx) > 0:
                predominant_idx = predominant_idx[0]
                return self.stems[predominant_idx]
            else:
                return None
        else:
            return None

    def load_melody_annotations(self):
        """Get melody annotations if files exists.
        """
        melody1_fname = _MELODY1_FMT % self.track_id
        melody2_fname = _MELODY2_FMT % self.track_id
        melody3_fname = _MELODY3_FMT % self.track_id

        melody1_fpath = os.path.join(self.annotation_dir, melody1_fname)
        melody2_fpath = os.path.join(self.annotation_dir, melody2_fname)
        melody3_fpath = os.path.join(self.annotation_dir, melody3_fname)

        self.melody1_annotation, _ = read_annotation_file(
            melody1_fpath, header=False
        )
        self.melody2_annotation, _ = read_annotation_file(
            melody2_fpath, header=False
        )
        self.melody3_annotation, _ = read_annotation_file(
            melody3_fpath, header=False
        )

    def _get_activation_annotations(self):
        """Get activation confidence annotation if file exists.
        """
        fname = _ACTIVCONF_FMT % self.track_id
        activation_annotation_fpath = os.path.join(self.annotation_dir, fname)
        activations, header = read_annotation_file(
            activation_annotation_fpath, header=True
        )
        idx_dict = {}
        for i, stem_str in enumerate(header):
            if stem_str == 'time':
                continue
            else:
                stem_idx = format_index(stem_str)
                idx_dict[stem_idx] = i
        return activations, idx_dict

    def melody_stems(self):
        """Get list of stems that contain melody.

        Returns:
            List of track objects where component='melody'.

        """
        stem_objects = self.stems.values()
        return [track for track in stem_objects if track.component == 'melody']

    def bass_stems(self):
        """Get list of stems that contain bass.

        Returns:
            List of track objects where component='bass'.

        """
        stem_objects = self.stems.values()
        return [track for track in stem_objects if track.component == 'bass']

    def num_stems(self):
        """Number of stems.

        Returns:
            Number of stems (as an int).

        """
        return len(self.stems)

    def num_raw(self):
        """Number of raw audio files.

        Returns:
            Number of raw audio files (as an int).

        """
        return len(get_dict_leaves(self.raw_audio))

    def stem_filepaths(self):
        """Get list of filepaths to stem files.

        Returns:
            List of filepaths to stems.

        """
        return [track.file_path for track in self.stems.values()]

    def raw_filepaths(self):
        """Get list of filepaths to raw audio files.

        Returns:
            List of filepaths to raw audio files.

        """
        return [track.file_path for track in get_dict_leaves(self.raw_audio)]

    def activation_conf_from_stem(self, stem_idx):
        """Get activation confidence from given stem.

        Args:
            stem_idx (int): stem index (eg. 2 for stem S02)

        Returns:
            activation_confidence (list): time and activation confidence

        """
        activations = []
        if stem_idx in self.stem_activations_idx:
            activ_conf_idx = self.stem_activations_idx[stem_idx]
            for step in self.stem_activations:
                activations.append([step[0], step[activ_conf_idx]])
        else:
            activations = None

        return activations


class Track(object):
    """Track class definition.

    Used for stems and for raw audio tracks.

    Attributes:
        component (str): One of ['melody', 'bass', ''].
        duration (float): Length of corresponding audio file (in seconds).
        file_path (str): Path to corresponding audio file.
        instrument (str): Instrument label.
        mix_path (str): Path to tracks corresponding mix file.
        pitch_annotation (list): List of time, f0 values.
        raw_idx (int): Index of corresponding raw audio file (None if a stem)
        stem_idx (int): Index of corresponding stem file.
        ranking (int): track's melody ranking

    """

    def __init__(self, instrument, file_path, stem_idx, mix_path,
                 pitch_path=None, raw_idx=None, component='', ranking=None,
                 mix_coeff=None):
        """Track object __init__ method.

        Args:
            instrument (str): the track's instrument label.
            file_path (str): path to corresponding audio file.
            component (str, optional): stem's component label, if exists.
            stem_idx (int or str): stem index, either as int or str
                For ArtistName_TrackTitle_STEM_05.wav, either 5 or 'S05'
            raw_idx (int or str, optional): raw index, either as int or str
                For ArtistName_TrackTitle_RAW_05_02.wav, either 2 or 'R02'
            mix_path (str): path to corresponding mix audio file.
            pitch_path (str, optional): path to pitch annotation directory
        """
        self.instrument = instrument
        self.f0_type = self._get_f0_type(instrument)
        self.file_path = file_path
        self.component = component
        self.ranking = ranking
        self.stem_idx = format_index(stem_idx)
        self.raw_idx = format_index(raw_idx)
        self.mixing_coefficient = mix_coeff

        if file_path is not None and os.path.exists(file_path):
            self.duration = get_duration(file_path)
        else:
            self.duration = None
        self.mix_path = mix_path
        self.pitch_annotation = None
        self._pitch_path = pitch_path

    def get_pitch_annotation(self):
        """Get pitch annotation if file exists.
        """
        if (self._pitch_path is not None) and (self.pitch_annotation is None):
            self.pitch_annotation, _ = read_annotation_file(
                self._pitch_path, num_cols=2, header=False
            )
        return self.pitch_annotation

    def _get_f0_type(self, instrument):
        if instrument in set(INST_F0_TYPE.keys()):
            return INST_F0_TYPE[instrument]
        else:
            return "?"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def __hash__(self):
        return hash((self.instrument,
                     self.file_path,
                     self.component,
                     self.stem_idx,
                     self.raw_idx,
                     self.mix_path,
                     self._pitch_path))


def _path_basedir(path):
    """Get the name of the lowest directory of a path.
    """
    norm_path = os.path.normpath(path)
    return os.path.basename(norm_path)


def format_index(index):
    """Load stem or raw index. Reformat if in string form.
    """
    if isinstance(index, str):
        return int(index.strip('S').strip('R'))
    elif index is None:
        return None
    else:
        return int(index)


def get_dict_leaves(dictionary):
    """Get the set of all leaves of a dictionary.

    Args:
        dictionary (dict): Any dictionary.

    Returns:
        vals (set): Set of leaf values.

    """
    vals = []
    if isinstance(dictionary, dict):
        for k in dictionary:
            if isinstance(dictionary[k], dict):
                for val in get_dict_leaves(dictionary[k]):
                    vals.append(val)
            else:
                if hasattr(dictionary[k], '__iter__'):
                    for val in dictionary[k]:
                        vals.append(val)
                else:
                    vals.append(dictionary[k])
    else:
        for val in dictionary:
            vals.append(val)

    return set(vals)


def get_duration(wave_fpath):
    """Return the duration of a wave file, in seconds.

    Example:
        >>> get_duration('my_favorite_song.wav')
        17.46267573696145

    Args:
        wave_fpath (str): Wave file.

    Returns:
        duration (float): Duration of wave file in seconds.

    """
    fpath = wave.open(wave_fpath, 'rb')
    nsamples = fpath.getnframes()
    sample_rate = fpath.getframerate()
    fpath.close()
    return float(nsamples) / float(sample_rate)


def read_annotation_file(fpath, num_cols=None, header=False):
    """Read an annotation file.

    Examples:
        >>> melody_fpath = 'ArtistName_TrackTitle_MELODY1.txt'
        >>> pitch_fpath = 'my_tony_pitch_annotation.csv'
        >>> melody_annotation, _ = read_annotation_file(melody_fpath)
        >>> activation_annotation, header = read_annotation_file(
                actvation_fpath, header=True
            )
        >>> pitch_annotation, _ = read_annotation_file(pitch_fpath, num_cols=2)

        The returned annotations can be directly converted to a numpy array,
            if desired.

    Note:
        When reading files generated by Tony, set num_cols=2.
        Annotation files created by Tony can contain a third column that
        sometimes has a value (e.g [2]) and sometimes does not. It isn't
        important for annotation and can be ignored.

    Args:
        fpath (str): Path to annotation file.
        num_cols (int, optionals): Number of columns to read. If specified,
            will only read the return num_cols columns of the annotation file.

    Returns:
        annotation (list): List of rows of the annotation file.
        header (list): Header row. Empty list if header=False.

    """
    if os.path.exists(fpath):
        with open(fpath) as f_handle:
            annotation = []
            linereader = csv.reader(f_handle)

            # skip the headers for non csv files
            if header:
                header = next(linereader)
            else:
                header = []

            for line in linereader:
                if num_cols:
                    line = line[:num_cols]
                annotation.append([float(val) for val in line])
        return annotation, header
    else:
        print("Warning: %s does not exist." % fpath)
        return None, None


def get_valid_instrument_labels(taxonomy=INST_TAXONOMY):
    """Get set of valid instrument labels based on a taxonomy.

    Examples:
        >>> valid_labels = get_valid_instrument_labels()
        >>> my_valid_labels = get_valid_instrument_labels('my_taxonomy.yaml')

    Args:
        taxonomy_file (str, optional): Path to instrument taxonomy file.

    Returns:
        valid_instrument_labels (set): Set of valid instrument labels.

    """
    valid_instrument_labels = get_dict_leaves(taxonomy)
    return valid_instrument_labels


def is_valid_instrument(instrument):
    """Test if an instrument is valid based on a taxonomy.
        This is case sensitive! Taxonomy instrument labels are all lowercase.

    Examples:
        >>> is_valid_instrument('clarinet')
        True
        >>> is_valid_instrument('Clarinet')
        False
        >>> is_valid_instrument('mayonnaise')
        False

    Args:
        instrument (str): Input instrument.

    Returns:
        value (bool): True if instrument is valid.

    """
    return instrument in get_valid_instrument_labels()
