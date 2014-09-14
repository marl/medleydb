"""Class definitions for MedleyDB multitracks.
"""

import os
import yaml
import wave
from . import INST_TAXONOMY
from . import PITCH_DIR
from . import MELODY_DIR


class MultiTrack(object):
    """ MultiTrack Class definition.
    """

    def __init__(self, mtrack_dir):

        # Artist, Title & Track Directory #
        self.mtrack_dir = mtrack_dir
        self.artist = os.path.basename(mtrack_dir.strip('/')).split('_')[0]
        self.title = os.path.basename(mtrack_dir.strip('/')).split('_')[1]
        self.track_id = "%s_%s" % (self.artist, self.title)

        # Filenames and Filepaths #
        self._meta_basename = "%s_METADATA.yaml" % self.track_id
        self._meta_path = os.path.join(mtrack_dir, self._meta_basename)
        self._stem_dir_basename = "%s_STEMS" % self.track_id
        self._stem_dir_path = os.path.join(mtrack_dir, self._stem_dir_basename)
        self._raw_dir_basename = "%s_RAW" % self.track_id
        self._raw_dir_path = os.path.join(mtrack_dir, self._raw_dir_basename)
        self._mix_basename = "%s_MIX.wav" % self.track_id
        self.mix_path = os.path.join(mtrack_dir, self._mix_basename)

        # Stem & Raw File Formats #
        self._stem_fmt = "%s_STEM_%%s.wav" % self.track_id
        self._raw_fmt = "%s_RAW_%%s_%%s.wav" % self.track_id

        # Yaml Dictionary of Metadata #
        self._metadata = self._load_metadata()

        # Stem & Raw Dictionaries. Lists of filepaths. #
        self.stems, self.raw_audio = self._parse_metadata()

        # Lists of Instrument Labels #
        self.stem_instruments = [s.instrument for s in self.stems]
        self.raw_instruments = [r.instrument for r in self.raw_audio]

        # Basic Track Information #
        self.duration = get_duration(self.mix_path)
        self.is_excerpt = _yn_to_tf(self._metadata['excerpt'])
        self.has_bleed = _yn_to_tf(self._metadata['has_bleed'])
        self.is_instrumental = _yn_to_tf(self._metadata['instrumental'])
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
        f_in = open(self._meta_path)
        metadata = yaml.load(f_in)
        f_in.close()
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
        melody1_fname = "%s_MELODY1.csv" % self.track_id
        melody2_fname = "%s_MELODY2.csv" % self.track_id
        melody3_fname = "%s_MELODY3.csv" % self.track_id

        melody1_fpath = os.path.join(MELODY_DIR, 'MELODY1', melody1_fname)
        melody2_fpath = os.path.join(MELODY_DIR, 'MELODY2', melody2_fname)
        melody3_fpath = os.path.join(MELODY_DIR, 'MELODY3', melody3_fname)

        self.melody1_annotation = read_csv_file(melody1_fpath)
        self.melody2_annotation = read_csv_file(melody2_fpath)
        self.melody3_annotation = read_csv_file(melody3_fpath)

    def melody_tracks(self):
        """ Get list of tracks that contain melody
        """
        track_list = []
        for track in self.stems:
            if track.component == 'melody':
                track_list.append(track)
        return track_list

    def bass_tracks(self):
        """ Get list of tracks that contain bass
        """
        track_list = []
        for track in self.stems:
            if track.component == 'bass':
                track_list.append(track)
        return track_list

    def num_stems(self):
        """ Number of stems.
        """
        return len(self.stems)

    def num_raw(self):
        """ Number of raw audio files.
        """
        return len(self.raw_audio)

    def stem_filepaths(self):
        """ Get list of filepaths to raw audio files.
        """
        filepaths = []
        for track in self.stems:
            filepaths.append(track.file_path)
        return filepaths

    def raw_filepaths(self):
        """ Get list of filepaths to raw audio files.
        """
        filepaths = []
        for track in self.raw_audio:
            filepaths.append(track.file_path)
        return filepaths

    def raw_from_stem(self, stem_idx):
        """ Get all raw audio tracks for a given stem index.
        """
        tracks = []
        for track in self.raw_audio:
            if track.stem_idx == stem_idx:
                tracks.append(track)
        return tracks

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
        fname = "%s.csv" % os.path.basename(self.file_path).split('.')[0]
        pitch_annotation_fpath = os.path.join(PITCH_DIR, fname)
        self.pitch_annotation = read_csv_file(pitch_annotation_fpath, maxcols=2)


def _yn_to_tf(yesno):
    """ Convert strings 'yes' and 'no' to booleans.
    """
    truefalse = None
    if yesno == 'yes':
        truefalse = True
    elif yesno == 'no':
        truefalse = False

    return truefalse


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
    """Compute duration of an audio file in seconds.

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
    f_handle = open(taxonomy_file)
    taxonomy = yaml.load(f_handle)
    f_handle.close()
    instrument_list = _get_dict_leaves(taxonomy)
    return instrument_list


def is_valid_instrument(instrument):
    """Test if an instrument instrument is valid based on a taxonomy.

    Parameters
    ----------
    instrument : str
        Input instrument instrument.

    Returns
    -------
    bool
        True if instrument is valid.
    """
    valid_instruments = get_valid_instrument_labels()
    return instrument in valid_instruments
