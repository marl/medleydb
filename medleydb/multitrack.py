"""Class definitions for MedleyDB multitracks.
"""

import os
import yaml
import wave
from . import INST_TAXONOMY
from . import PITCH_DIR
from . import MELODY_DIR

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
_PITCH_FMT = "%s.csv"


class MultiTrack(object):
    """ MultiTrack Class definition.
    """

    def __init__(self, mtrack_dir):

        # Artist, Title & Track Directory #
        self.mtrack_dir = mtrack_dir
        self.artist = _path_basedir(mtrack_dir).split('_')[0]
        self.title = _path_basedir(mtrack_dir).split('_')[1]
        self.track_id = _TRACKID_FMT % (self.artist, self.title)

        # Filenames and Filepaths #
        self._meta_basename = _METADATA_FMT % self.track_id
        self._meta_path = os.path.join(mtrack_dir, self._meta_basename)
        self._stem_dir_basename = _STEMDIR_FMT % self.track_id
        self._stem_dir_path = os.path.join(mtrack_dir, self._stem_dir_basename)
        self._raw_dir_basename = _RAWDIR_FMT % self.track_id
        self._raw_dir_path = os.path.join(mtrack_dir, self._raw_dir_basename)
        self._mix_basename = _MIX_FMT % self.track_id
        self.mix_path = os.path.join(mtrack_dir, self._mix_basename)

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
        self.melody1_annotation = []
        self.melody2_annotation = []
        self.melody3_annotation = []
        self._fill_melody_annotations()

    def _load_metadata(self):
        """ Load the metadata file.
        """
        with open(self._meta_path, 'r') as f_in:
            metadata = yaml.load(f_in)
        return metadata

    def _parse_metadata(self):
        """ Parse metadata dictionary into useful things.
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
                          component=component, stem_idx=k,
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

    def _fill_melody_annotations(self):
        """ Fill melody annotations if files exists
        """
        melody1_fname = _MELODY1_FMT % self.track_id
        melody2_fname = _MELODY2_FMT % self.track_id
        melody3_fname = _MELODY3_FMT % self.track_id

        melody1_fpath = os.path.join(MELODY_DIR, _MELODY1_DIR, melody1_fname)
        melody2_fpath = os.path.join(MELODY_DIR, _MELODY2_DIR, melody2_fname)
        melody3_fpath = os.path.join(MELODY_DIR, _MELODY3_DIR, melody3_fname)

        self.melody1_annotation = read_csv_file(melody1_fpath)
        self.melody2_annotation = read_csv_file(melody2_fpath)
        self.melody3_annotation = read_csv_file(melody3_fpath)

    def melody_tracks(self):
        """ Get list of tracks that contain melody """
        return [track for track in self.stems if track.component == 'melody']

    def bass_tracks(self):
        """ Get list of tracks that contain bass """
        return [track for track in self.stems if track.component == 'bass']

    def num_stems(self):
        """ Number of stems. """
        return len(self.stems)

    def num_raw(self):
        """ Number of raw audio files. """
        return len(self.raw_audio)

    def stem_filepaths(self):
        """ Get list of filepaths to raw audio files. """
        return [track.file_path for track in self.stems]

    def raw_filepaths(self):
        """ Get list of filepaths to raw audio files. """
        return [track.file_path for track in self.raw_audio]

    def raw_from_stem(self, stem_idx):
        """ Get all raw audio tracks for a given stem index. """
        return [track for track in self.raw_audio if track.stem_idx == stem_idx]

class Track(MultiTrack):
    """ Track class definition.
    """
    def __init__(self, instrument='', file_path='', component='',
                 stem_idx=None, raw_idx=None, mix_path =''):
        self.instrument = instrument
        self.file_path = file_path
        self.component = component
        self.stem_idx = stem_idx
        self.raw_idx = raw_idx
        self.duration = get_duration(file_path)
        self.mix_path = mix_path
        self.pitch_annotation = None

        if self.component == 'melody':
            self._fill_pitch_annotation()

    def _fill_pitch_annotation(self):
        """ Fill pitch annotation if file exists.
        """
        fname = _PITCH_FMT % os.path.basename(self.file_path).split('.')[0]
        pitch_annotation_fpath = os.path.join(PITCH_DIR, fname)
        self.pitch_annotation = read_csv_file(pitch_annotation_fpath, maxcols=2)


def _path_basedir(path):
    """ Get the name of the lowest directory of a path
    """
    norm_path = os.path.normpath(path)
    return os.path.basename(norm_path)


def _get_dict_leaves(dictionary):
    """Get the set of all leaves of a dictionary.

    Parameters
    ----------
    dictionary : dict
        Any dictionary.

    Returns
    -------
    vals : set
        Set of leaf values.
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


def get_duration(fname):
    """Return the file duration, in seconds.

    Parameters
    ----------
    fname : str
        Audio file.

    Returns
    -------
    duration : float
        Duration of audio file in seconds.
    """
    fpath = wave.open(fname, 'rb')
    nsamples = fpath.getnframes()
    sample_rate = fpath.getframerate()
    fpath.close()
    return float(nsamples)/float(sample_rate)


def read_csv_file(fpath, maxcols=None):
    """ Read a csv file.
    """
    if os.path.exists(fpath):
        data_lines = [line.strip() for line in open(fpath)]
        annotation = []
        for line in data_lines:
            if maxcols:
                row = line.split(',')[0:maxcols]
            else:
                row = line.split(',')
            annotation.append([float(val) for val in row])
        return annotation
    else:
        return None

def get_valid_instrument_labels(taxonomy_file=INST_TAXONOMY):
    """Get set of valid instrument labels based on a taxonomy.

    Parameters
    ----------
    taxonomy_file : str
        Path to instrument taxonomy file.

    Returns
    -------
    instrument_list : set
        Set of valid instrument labels.
    """
    with open(taxonomy_file) as f_handle:
        taxonomy = yaml.load(f_handle)
    instrument_list = _get_dict_leaves(taxonomy)
    return instrument_list


def is_valid_instrument(instrument):
    """Test if an instrument is valid based on a taxonomy.

    Parameters
    ----------
    instrument : str
        Input instrument.

    Returns
    -------
    value: bool
        True if instrument is valid.
    """
    return instrument in get_valid_instrument_labels()
