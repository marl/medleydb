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


def run_pyin(audio_fpath, save_dir):
    if not BINARY_AVAILABLE:
        raise EnvironmentError(
            "Either the vamp plugin {} needed to compute these contours or "
            "sonic-annotator is not available.".format(VAMP_PLUGIN)
        )

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


def main(args):
    """Run pyin on a medleydb stem or raw track
    """
    mtrack = medleydb.MultiTrack(args.track_id)
    for stem in mtrack.stems.values():
        if 'm' in stem.f0_type and not os.path.exists(stem.pitch_pyin_path):
            if os.path.exists(stem.audio_path):
                run_pyin(stem.audio_path, _PITCH_PYIN_PATH)
            else:
                print(
                    "[Warning] Audio not found for {}".format(stem.audio_path)
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("track_id",
                        type=str,
                        help="MedleyDB track id. Ex. MusicDelta_Rock")

    main(parser.parse_args())
