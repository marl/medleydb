#!/usr/bin/env python
"""Script to create stem level has_bleed annotations."""

from __future__ import print_function

import argparse
import librosa
import numpy as np

from medleydb.multitrack import MultiTrack


def load_audio(filepath, samplerate):
    y, sr = librosa.load(filepath, sr=samplerate)
    return y, sr


def make_audio_stack(mtrack, fs=22050):
    stems = mtrack.stems
    n_stems = len(stems)

    print("loading stem 1...")
    stem1_audio, fs = load_audio(stems[1].audio_path, fs)
    n_samples = len(stem1_audio)

    audio_stack = np.zeros((n_stems, n_samples))

    for stem_idx in stems:
        if stem_idx == 1:
            audio_stack[0, :] = stem1_audio
        else:
            print("loading stem %s..." % stem_idx)
            audio_path = stems[stem_idx].file_path
            audio_stack[stem_idx - 1, :], _ = load_audio(audio_path, fs)

    return audio_stack, fs, n_samples


def compute_bleed_estimation_matrix(audio_stack, fs, n_samples):
    # TODO
    pass


def main(args):
    mtrack = MultiTrack(args.track_id)
    audio_stack, fs, n_samples = make_audio_stack(mtrack)
    compute_bleed_estimation_matrix(audio_stack, fs, n_samples)
    # TODO save output to file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("track_id",
                        type=str,
                        help="MedleyDB track id. Ex. MusicDelta_Rock")
    parser.add_argument("write_output",
                        type=bool,
                        default=True,
                        help="If true, write the output to a file")

    main(parser.parse_args())
