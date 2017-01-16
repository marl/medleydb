"""Compute pyin output for all monophonic stems in multitracks without bleed.
"""
from __future__ import print_function

import medleydb
from medleydb import download
from medleydb import TRACK_LIST_V1
from medleydb import TRACK_LIST_V2
from medleydb import TRACK_LIST_EXTRA
import shutil
import sox
import tempfile

from medleydb.annotate.activation_conf import create_activation_annotation
from medleydb.annotate.activation_conf import write_activations_to_csv

import os


def ensure_samplerate(audio_path):
    samplerate = sox.file_info.sample_rate(audio_path)
    if samplerate != 44100:
        tfm = sox.Transformer()
        tfm.rate(44100)
        _, pyin_audio = tempfile.mkstemp(suffix='.wav')
        tfm.build(audio_path, pyin_audio)
        os.remove(audio_path)
        shutil.move(pyin_audio, audio_path)


def main():
    for track_id in TRACK_LIST_EXTRA + TRACK_LIST_V2 + TRACK_LIST_V1:
        print(track_id)
        try:
            mtrack = medleydb.MultiTrack(track_id)
            if mtrack.has_bleed or os.path.exists(mtrack.activation_conf_fpath):
                continue

            for stem in mtrack.stems.values():
                print(stem.stem_idx)
                download.download_stem(mtrack, stem.stem_idx)
                ensure_samplerate(stem.audio_path)

            activations, index_list = create_activation_annotation(mtrack)
            write_activations_to_csv(mtrack, activations, index_list, debug=True)

            download.purge_downloaded_files()
        except:
            print("Something failed...")


if __name__ == '__main__':
    main()
