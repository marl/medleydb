"""Compute pyin output for all monophonic stems in multitracks without bleed.
"""
from __future__ import print_function

import medleydb
from medleydb import download
from medleydb import TRACK_LIST_V1
from medleydb import TRACK_LIST_V2
from medleydb import TRACK_LIST_EXTRA
from medleydb.multitrack import _PITCH_PYIN_PATH
import shutil
import sox

from medleydb.annotate.generate_pyin_pitch_annotations import run_pyin
import os


def main():
    for track_id in TRACK_LIST_EXTRA + TRACK_LIST_V2 + TRACK_LIST_V1:
        print(track_id)
        try:
            mtrack = medleydb.MultiTrack(track_id)
            if mtrack.has_bleed:
                continue

            for stem in mtrack.stems.values():

                if not isinstance(stem.f0_type, list):
                    f0_type = [stem.f0_type]
                else:
                    f0_type = stem.f0_type

                if 'm' in f0_type and not os.path.exists(stem.pitch_pyin_path):
                    download.download_stem(mtrack, stem.stem_idx)
                    samplerate = sox.file_info.sample_rate(stem.audio_path)
                    if samplerate != 44100:
                        print("[SAMPLERATE] Check {}".format(track_id))
                        tfm = sox.Transformer()
                        tfm.rate(44100)
                        pyin_audio = 'dumbtempfile.wav'
                        tfm.build(stem.audio_path, pyin_audio)
                        os.remove(stem.audio_path)
                        shutil.move(pyin_audio, stem.audio_path)
                    run_pyin(stem.audio_path, _PITCH_PYIN_PATH)
                    download.purge_downloaded_files()
        except:
            print("Something failed...")


if __name__ == '__main__':
    main()
