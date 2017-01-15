"""Generate automatic pitch annotations using pyin
"""
from __future__ import print_function

import argparse
import os
import shutil
import subprocess
from subprocess import CalledProcessError

import medleydb
from medleydb import PYIN_N3_PATH
from medleydb.multitrack import _PITCH_PYIN_PATH

OUTPUT_FILE_STRING = "vamp_pyin_pyin_smoothedpitchtrack"
VAMP_PLUGIN = b"vamp:pyin:pyin:smoothedpitchtrack"


def _check_binary():
    '''Check if the vamp plugin is available and can be called.

    Returns
    -------
    True if callable, False otherwise
    '''
    sonic_annotator_exists = True
    try:
        subprocess.check_output(['which', 'sonic-annotator'])
    except CalledProcessError:
        sonic_annotator_exists = False

    if sonic_annotator_exists:
        avail_plugins = subprocess.check_output(["sonic-annotator", "-l"])
        if VAMP_PLUGIN in avail_plugins:
            return True
        else:
            return False
    else:
        return False


BINARY_AVAILABLE = _check_binary()


def pyin_call(audio_fpath, save_dir):
    '''Run pyin on an audio file and save results to a specified directory.
    
    Parameters
    ----------
    audio_fpath : str
        Path to audio file
    save_dir : str
        Path to save output

    Returns
    -------
    True on success
    '''
    if not BINARY_AVAILABLE:
        raise EnvironmentError(
            "Either the vamp plugin {} or "
            "sonic-annotator is not available.".format(VAMP_PLUGIN)
        )

    if not os.path.exists(audio_fpath):
        raise IOError("Audio path {} does not exist".format(audio_fpath))

    input_file_name = os.path.basename(audio_fpath)
    vamp_output_name = "{}_{}.csv".format(
        input_file_name.split('.')[0], OUTPUT_FILE_STRING
    )
    vamp_output_dir = os.path.dirname(audio_fpath)
    vamp_output_path = os.path.join(vamp_output_dir, vamp_output_name)

    args = [
        "sonic-annotator", "-t", PYIN_N3_PATH,
        "{}".format(audio_fpath), "-w", "csv", "--csv-force"
    ]
    os.system(' '.join(args))

    if not os.path.exists(vamp_output_path):
        raise IOError(
            "Unable to find vamp output file {}".format(vamp_output_path)
        )

    output_path = os.path.join(save_dir, vamp_output_name)

    shutil.move(vamp_output_path, output_path)

    return True


def get_pyin_annotation(mtrack, stem_id, raw_id=None):
    """Get pyin annotation for a stem or raw track for a multitrack.
    
    Parameters
    ----------
    mtrack : MultiTrack object
        Medleydb multitrack
    stem_id : int
        Stem id to annotate
    raw_id : int or None, default=None
        Raw id to annotate, or None to annotate a stem

    Raises
    ------
    ValueError on invalid stem or raw ids
    """
    if stem_id in mtrack.stems.keys():
        stem = mtrack.stems[stem_id]
    else:
        raise ValueError("Invalid stem id {}".format(stem_id))

    if raw_id is not None and raw_id in mtrack.raw_audio[stem_id].keys():
        raw = mtrack.raw_audio[stem_id]
        pyin_call(raw.audio_path, _PITCH_PYIN_PATH)  # run pyin on raw track
    elif raw_id is None:
        pyin_call(stem.audio_path, _PITCH_PYIN_PATH)  # run pyin on stem
    else:
        raise ValueError("Invalid raw id {}".format(raw_id))


def main(args):
    """Run pyin on a medleydb stem or raw track.
    """
    mtrack = medleydb.MultiTrack(args.track_id)
    stem_id = args.stem_id
    raw_id = args.raw_id

    get_pyin_annotation(mtrack, stem_id, raw_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("track_id",
                        type=str,
                        help="MedleyDB track id. Ex. MusicDelta_Rock")
    parser.add_argument("stem_id",
                        type=int,
                        help="stem_id to annotate")
    parser.add_argument("raw_id",
                        type=int,
                        default=None,
                        help="raw_id to annotate. If none, annotates the stem")

    main(parser.parse_args())
