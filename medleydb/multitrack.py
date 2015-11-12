#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class definitions for MedleyDB multitracks."""

import os
import yaml
import wave
import csv
from . import INST_TAXONOMY
from . import PITCH_DIR
from . import MELODY_DIR
from . import ACTIVATIONS_DIR
from . import RANKINGS_DIR

_YESNO = dict(yes=True, no=False)
_TRACKID_FMT = "%s_%s"
_METADATA_FMT = "%s_METADATA.yaml"
_STEMDIR_FMT = "%s_STEMS"
_RAWDIR_FMT = "%s_RAW"
_MIX_FMT = "%s_MIX.wav"
_STEM_FMT = "%s_STEM_%%s.wav"
_RAW_FMT = "%s_RAW_%%s_%%s.wav"
_MELODY1_DIR = 'MELODY1'
_MELODY2_DIR = 'MELODY2'
_MELODY3_DIR = 'MELODY3'
_MELODY1_FMT = "%s_MELODY1.csv"
_MELODY2_FMT = "%s_MELODY2.csv"
_MELODY3_FMT = "%s_MELODY3.csv"
_RANKING_FMT = "%s_RANKING.txt"
_ACTIVATION_CONFS_DIR = 'ACTIVATION_CONF'
_ACTIVATION_CONFS_FMT = "%s_ACTIVATION_CONF.lab"
_PITCH_FMT = "%s.csv"


class MultiTrack(object):
    """MultiTrack Class definition.

    This class loads all available metadata, annotations, and filepaths for a
    given multitrack directory.

    Examples:
        >>> mtrack = Multitrack('/MedleyDB/Audio/LizNelson_Rainfall')
        >>> another_mtrack = Multitrack('some/path/ArtistName_TrackTitle')

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

    def __init__(self, mtrack_path):
        """MultiTrack object __init__ method.

        Args:
            mtrack_path (str): Path to folder with multitrack information.

        """

        # Artist, Title & Track Directory #
        self.mtrack_path = mtrack_path
        self.artist = _path_basedir(mtrack_path).split('_')[0]
        self.title = _path_basedir(mtrack_path).split('_')[1]
        self.track_id = _TRACKID_FMT % (self.artist, self.title)

        # Filenames and Filepaths #
        self._meta_basename = _METADATA_FMT % self.track_id
        self._meta_path = os.path.join(mtrack_path, self._meta_basename)
        self._stem_dir_basename = _STEMDIR_FMT % self.track_id
        self._stem_dir_path = os.path.join(
            mtrack_path,
            self._stem_dir_basename
        )
        self._raw_dir_basename = _RAWDIR_FMT % self.track_id
        self._raw_dir_path = os.path.join(mtrack_path, self._raw_dir_basename)
        self._mix_basename = _MIX_FMT % self.track_id
        self.mix_path = os.path.join(mtrack_path, self._mix_basename)

        # Stem & Raw File Formats #
        self._stem_fmt = _STEM_FMT % self.track_id
        self._raw_fmt = _RAW_FMT % self.track_id

        # Yaml Dictionary of Metadata #
        self._metadata = self._load_metadata()

        # Stem & Raw Dictionaries. Lists of filepaths. #
        self.stems, self.raw_audio = self._parse_metadata()

        # Lists of Instrument Labels #
        self.stem_instruments = [s.instrument for s in self.stems]
        self.raw_instruments = [r.instrument for r in self.raw_audio]

        # Basic Track Information #
        self.duration = get_duration(self.mix_path)
        self.is_excerpt = _YESNO[self._metadata['excerpt']]
        self.has_bleed = _YESNO[self._metadata['has_bleed']]
        self.is_instrumental = _YESNO[self._metadata['instrumental']]
        self.origin = self._metadata['origin']
        self.genre = self._metadata['genre']

        # Annotations
        (
            self.melody1_annotation,
            self.melody2_annotation,
            self.melody3_annotation
        ) = self._get_melody_annotations()
        self.predominant_stem = self._get_predominant_stem()
        self.stem_activations = self._get_activation_annotations()

    def _load_metadata(self):
        """Load the metadata file.
        """
        with open(self._meta_path, 'r') as f_in:
            metadata = yaml.load(f_in)
        return metadata

    def _parse_metadata(self):
        """Parse metadata dictionary.
        """
        stems = []
        raw_audio = []
        stem_dict = self._metadata['stems']

        for k in stem_dict.keys():
            instrument = stem_dict[k]['instrument']
            component = stem_dict[k]['component']
            file_name = stem_dict[k]['filename']
            file_path = os.path.join(self._stem_dir_path, file_name)

            track = Track(instrument=instrument, file_path=file_path,
                          component=component, stem_idx=k[1:],
                          mix_path=self.mix_path)

            stems.append(track)
            raw_dict = stem_dict[k]['raw']

            for j in raw_dict.keys():
                instrument = raw_dict[j]['instrument']
                file_name = raw_dict[j]['filename']
                file_path = os.path.join(self._raw_dir_path, file_name)

                track = Track(instrument=instrument, file_path=file_path,
                              stem_idx=k[1:], raw_idx=j[1:],
                              mix_path=self.mix_path)
                raw_audio.append(track)

        return stems, raw_audio

    def _get_melody_annotations(self):
        """Get melody annotations if files exists.
        """
        melody1_fname = _MELODY1_FMT % self.track_id
        melody2_fname = _MELODY2_FMT % self.track_id
        melody3_fname = _MELODY3_FMT % self.track_id

        melody1_fpath = os.path.join(MELODY_DIR, _MELODY1_DIR, melody1_fname)
        melody2_fpath = os.path.join(MELODY_DIR, _MELODY2_DIR, melody2_fname)
        melody3_fpath = os.path.join(MELODY_DIR, _MELODY3_DIR, melody3_fname)

        return (
            read_annotation_file(melody1_fpath),
            read_annotation_file(melody2_fpath),
            read_annotation_file(melody3_fpath)
        )

    def _get_activation_annotations(self):
        """Get activation confidence annotation if file exists.
        """
        fname = _ACTIVATION_CONFS_FMT % self.track_id
        activation_annotation_fpath = os.path.join(
            ACTIVATIONS_DIR, _ACTIVATION_CONFS_DIR, fname
        )
        return read_annotation_file(activation_annotation_fpath)

    def _get_predominant_stem(self):
        """Get predominant stem if files exists.
        """
        rankings_fname = _RANKING_FMT % self.track_id
        rankings_fpath = os.path.join(RANKINGS_DIR, rankings_fname)

        # self.predominant_stem = read_annotation_file(rankings_fpath)
        if os.path.exists(rankings_fpath):
            with open(rankings_fpath) as f_handle:
                linereader = csv.reader(f_handle)
                for line in linereader:
                    if line[1] == '1':
                        stem_dict = self._metadata['stems']
                        s = line[0].split('_')[-1].split('.')[0]

                        instrument = stem_dict['S' + s]['instrument']
                        component = stem_dict['S' + s]['component']
                        file_name = stem_dict['S' + s]['filename']
                        file_path = os.path.join(
                            self._stem_dir_path, file_name
                        )

                        track = Track(
                            instrument=instrument,
                            file_path=file_path,
                            component=component,
                            stem_idx='S' + s,
                            mix_path=self.mix_path
                        )

                        return track
        return None

    def melody_tracks(self):
        """Get list of tracks that contain melody.

        Returns:
            List of track objects where component='melody'.

        """
        return [track for track in self.stems if track.component == 'melody']

    def bass_tracks(self):
        """Get list of tracks that contain bass.

        Returns:
            List of track objects where component='bass'.

        """
        return [track for track in self.stems if track.component == 'bass']

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
        return len(self.raw_audio)

    def stem_filepaths(self):
        """Get list of filepaths to stem files.

        Returns:
            List of filepaths to stems.

        """
        return [track.file_path for track in self.stems]

    def raw_filepaths(self):
        """Get list of filepaths to raw audio files.

        Returns:
            List of filepaths to raw audio files.

        """
        return [track.file_path for track in self.raw_audio]

    def raw_from_stem(self, stem_idx):
        """Get all raw audio tracks that are children of a given stem.

        Args:
            stem_idx (int): stem index (eg. 2 for stem S02)

        Returns:
            List of Track objects.

        """
        return [
            track for track in self.raw_audio if track.stem_idx == stem_idx
        ]

    def activation_conf_from_stem(self, stem_idx):
        """Get all raw audio tracks that are children of a given stem.

        Args:
            stem_idx (int): stem index (eg. 2 for stem S02)

        Returns:
            activation_confidence (list): time and activation confidence

        """

        activations = []
        for step in self.stem_activations:
            activations.append([step[0], step[stem_idx]])

        return activations


class Track(object):
    """Track class definition.

    Used for stems and for raw audio tracks.

    Attributes:
        component (str): Description of `attr3`.
        duration (float): Length of corresponding audio file (in seconds).
        file_path (str): Path to corresponding audio file.
        instrument (str): Instrument label.
        mix_path (str): Path to tracks corresponding mix file.
        pitch_annotation (list): List of time, f0 values.
        raw_idx (int): Index of corresponding raw audio file (None if a stem)
        stem_idx (int): Index of corresponding stem file.

    """

    def __init__(self, instrument='', file_path='', component='',
                 stem_idx=None, raw_idx=None, mix_path=''):
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
        """
        self.instrument = instrument
        self.file_path = file_path
        self.component = component
        self.stem_idx = self._format_index(stem_idx)
        self.raw_idx = self._format_index(raw_idx)
        self.duration = get_duration(file_path)
        self.mix_path = mix_path
        self.pitch_annotation = None

        if self.component == 'melody':
            self.pitch_annotation = self._get_pitch_annotation()

    def _format_index(self, index):
        """Load stem or raw index. Reformat if in string form.
        """
        if isinstance(index, str):
            return int(index.strip('S').strip('R'))
        elif index is None:
            return None
        else:
            return int(index)

    def _get_pitch_annotation(self):
        """Get pitch annotation if file exists.
        """
        fname = _PITCH_FMT % os.path.basename(self.file_path).split('.')[0]
        pitch_annotation_fpath = os.path.join(PITCH_DIR, fname)
        return read_annotation_file(pitch_annotation_fpath,
                                    num_cols=2)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def _path_basedir(path):
    """Get the name of the lowest directory of a path.
    """
    norm_path = os.path.normpath(path)
    return os.path.basename(norm_path)


def _get_dict_leaves(dictionary):
    """Get the set of all leaves of a dictionary.

    Args:
        dictionary (dict): Any dictionary.

    Returns:
        vals (set): Set of leaf values.

    """
    vals = []
    if type(dictionary) == dict:
        keys = dictionary.keys()
        for k in keys:
            if type(dictionary[k]) == dict:
                for val in _get_dict_leaves(dictionary[k]):
                    vals.append(val)
            else:
                for val in dictionary[k]:
                    vals.append(val)
    else:
        for val in dictionary:
            vals.append(val)

    vals = set(vals)
    return vals


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


def read_annotation_file(fpath, num_cols=None):
    """Read an annotation file.

    Examples:
        >>> melody_fpath = 'ArtistName_TrackTitle_MELODY1.txt'
        >>> pitch_fpath = 'my_tony_pitch_annotation.csv'
        >>> melody_annotation = read_annotation_file(melody_fpath)
        >>> activation_annotation = read_annotation_file(actvation_fpath)
        >>> pitch_annotation = read_annotation_file(pitch_fpath, num_cols=2)

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

    """
    if os.path.exists(fpath):
        with open(fpath) as f_handle:
            annotation = []
            linereader = csv.reader(f_handle)

            # skip the headers for non csv files
            if os.path.splitext(fpath)[1] == '.lab':
                next(linereader, None)

            for line in linereader:
                if num_cols:
                    line = line[:num_cols]
                annotation.append([float(val) for val in line])
        return annotation
    else:
        return None


def get_valid_instrument_labels(taxonomy_file=INST_TAXONOMY):
    """Get set of valid instrument labels based on a taxonomy.

    Examples:
        >>> valid_labels = get_valid_instrument_labels()
        >>> my_valid_labels = get_valid_instrument_labels('my_taxonomy.yaml')

    Args:
        taxonomy_file (str, optional): Path to instrument taxonomy file.

    Returns:
        valid_instrument_labels (set): Set of valid instrument labels.

    """
    with open(taxonomy_file) as f_handle:
        taxonomy = yaml.load(f_handle)
    valid_instrument_labels = _get_dict_leaves(taxonomy)
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
