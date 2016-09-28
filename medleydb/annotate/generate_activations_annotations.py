from __future__ import division
import scipy.signal
import numpy as np
import librosa
import medleydb
import os
import csv
import argparse
import soundfile as sf


def create_activation_annotation(
    mtrack,
    win_len=2048,
    lpf_cutoff=0.075,
    theta=.4,
    binarize=False
):

    H = []

    for track_id, track in mtrack.stems.items():
        audio, rate = sf.read(track.file_path)
        H.append(track_activation(audio, win_len))

    # list to numpy array
    H = np.array(H)
    # normalization (to overall energy and # of sources)

    E0 = np.sum(H, axis=0)

    H = len(mtrack.stems) * H / np.max(E0)

    # binary thresholding for low overall energy events
    mask = np.ones(H.shape)
    mask[:, E0 < 0.01] = 0
    H = H * mask

    # LP filter
    b, a = scipy.signal.butter(2, lpf_cutoff, 'low')
    H = scipy.signal.filtfilt(b, a, H, axis=1)

    # logistic function to semi-binarize the output; confidence value
    H = 1 - 1 / (1 + np.exp(np.dot(20, (H-theta))))

    # binarize output
    if binarize:
        H_out = np.zeros(H.shape)
        H_out[H > 0.5] = 1
    else:
        H_out = H

    return H_out


def track_activation(wave, win_len):

    # Parameters
    hop_len = win_len // 2
    win = np.hanning(win_len)

    # mix down to 1 channel
    wave = np.mean(wave, axis=1)

    wavmat = librosa.util.frame(wave, frame_length=win_len, hop_length=hop_len)

    # Envelope follower
    wavmat = hwr(wavmat) ** 0.5  # half-wave rectification + compression

    return np.mean((wavmat.T * win), axis=1)


def hwr(x):
    ''' half-wave rectification'''
    return (x + np.abs(x)) / 2


def write_activations_to_csv(mtrack, activations):

    activation_fname = "%s_ACTIVATION_CONF.lab" % mtrack.track_id

    activations_fpath = os.path.join(mtrack.annotation_dir, activation_fname)
    return activations_fpath


def main(args):
    mtrack = medleydb.MultiTrack(args.track_id)
    activations = create_activation_annotation(mtrack)
    if args.write_output:
        write_activations_to_csv(mtrack, activations)


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
