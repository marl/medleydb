"""Script to create stem level has_bleed annotations."""
import argparse
import os
import csv

import numpy as np

import medleydb

import matplotlib.pyplot as plt


def load_audio(filepath, fs):
    # TODO write me
    return filepath, fs


def make_audio_stack(mtrack, fs=22050):
    stems = mtrack.stems
    n_stems = len(stems)

    print("loading stem 1...")
    stem1_audio, fs = load_audio(stems[1].file_path, fs)
    n_samples = len(stem1_audio)

    audio_stack = np.zeros((n_stems, n_samples))

    for stem_idx in list(stems.keys()):
        if stem_idx == 1:
            audio_stack[0, :] = stem1_audio
        else:
            print("loading stem %s..." % stem_idx)
            audio_path = stems[stem_idx].file_path
            audio_stack[stem_idx-1, :], _ = load_audio(audio_path, fs)

    return audio_stack, fs, n_samples


def compute_bleed_estimation_matrix(audio_stack, fs, n_samples):
    print("computing svd...")
    U, S, V = np.linalg.svd(audio_stack, full_matrices=False)
    plt.subplot(2,1,1)
    plt.imshow(U, interpolation='nearest')
    plt.colorbar()
    plt.subplot(2,1,2)
    plt.imshow(np.diag(S), interpolation='nearest')
    plt.colorbar()
    plt.show()

    # time_split = 30*fs
    # i = 0
    # while i < n_samples:
    #     




def main(args):
    mtrack = medleydb.MultiTrack(args.track_id)
    audio_stack, fs, n_samples = make_audio_stack(mtrack)
    compute_bleed_estimation_matrix(audio_stack, fs, n_samples)
    # melody1 = create_melody1_annotation(mtrack)
    # melody2 = create_melody2_annotation(mtrack)
    # melody3 = create_melody3_annotation(mtrack)
    # if args.write_output:
    #     write_melodies_to_csv(mtrack, melody1, melody2, melody3)


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