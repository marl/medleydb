#!/usr/bin/env python
"""Script to generate melody annotations from pitch annotations files"""

from __future__ import print_function

import argparse
import os
import csv
import numpy as np

import medleydb

HOP = 256.0  # samples
FS = 44100.0  # samples/second


def get_time_stamps(total_duration, fs, hop):
    """Get an array of evenly spaced time stamps.

    Parameters
    ----------
    total_duration : float
        Duration in seconds
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    time_stamps : np.array
        Array of evenly spaced time stamps.

    """
    time_stamps = []
    n_stamps = int(np.ceil((total_duration * fs) / hop))
    time_stamps = np.arange(n_stamps) * (hop / fs)
    return time_stamps


def make_blank_melody_sequence(total_duration, fs, hop):
    """Make a melody sequence with f0 values equal to 0.

    Parameters
    ----------
    total_duration : float
        Duration in seconds
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    melody_sequence : np.array
        A melody sequence with a column of time stamps and a column of zeros

    """
    time_stamps = get_time_stamps(total_duration, fs, hop)
    melody_sequence = np.zeros((len(time_stamps), 2))
    for i, time_stamp in enumerate(time_stamps):
        melody_sequence[i][0] = time_stamp
    return melody_sequence


def sec_to_idx(time_in_seconds, fs, hop):
    """Convert an array of times in seconds to the nearest evenly spaced indices

    Parameters
    ----------
    time_in_seconds : array-like
        Time values in seconds
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    time_idx : array-like
        Indices of closest time values

    """
    return int(np.round(time_in_seconds * float(fs) / float(hop)))


def add_sequence_to_melody(total_duration, f0_sequence, melody_sequence, fs,
                           hop, dim=1, start_t=0, end_t=-1):
    """Add an f0 sequence to a melody.

    Parameters
    ----------
    total_duration : float
        Track duration in seconds
    f0_sequence : list or None
        List of time (seconds), frequency (Hz) pairs
    melody_sequence : np.array
        Melody conainer. First column is time stamps
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)
    dim : int, default=1
        Column index to add melody sequence to
    start_t : float, default=0
        Start time of melody sequence
    end_t : float, default=-1
        End time of melody sequence. -1 defaults to track_duration

    Returns
    -------
    melody_sequence : np.array
        Sequence of melody values with newly added values

    """
    if start_t < 0:
        start_t = 0
    if end_t > total_duration:
        end_t = total_duration

    start_idx = sec_to_idx(start_t, fs, hop)
    if end_t == -1:
        end_idx = sec_to_idx(total_duration, fs, hop)
    else:
        end_idx = sec_to_idx(end_t, fs, hop)

    if f0_sequence:
        for time_freq in f0_sequence:
            time = time_freq[0]
            freq = time_freq[1]
            time_idx = sec_to_idx(time, fs, hop)
            if time_idx >= start_idx and time_idx < end_idx:
                melody_sequence[time_idx][dim] = freq

    return melody_sequence


def create_melody1_annotation(mtrack, fs=FS, hop=HOP):
    """Create a melody1 annotation from pitch annotations

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    melody1 : np.array or None
        Melody 1 annotation if a predominant stem exists, else None

    """
    predominant_stem = mtrack.predominant_stem

    if predominant_stem is not None:
        f0_annotation = predominant_stem.pitch_annotation
        print(f0_annotation)

        melody_sequence = make_blank_melody_sequence(mtrack.duration, fs, hop)
        melody1 = add_sequence_to_melody(
            mtrack.duration, f0_annotation, melody_sequence, fs, hop
        )
    else:
        melody1 = None

    return melody1


def create_melody2_annotation(mtrack, fs=FS, hop=HOP):
    """Create a melody2 annotation from pitch annotations

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    melody2 : np.array or None
        Melody 2 annotation if an intervals file exists, else None

    """
    if os.path.exists(mtrack.melody_intervals_fpath):

        intervals = []
        with open(mtrack.melody_intervals_fpath, 'rU') as fhandle:
            linereader = csv.reader(fhandle, delimiter='\t')

            for line in linereader:
                start_t = float(line[0])
                end_t = float(line[1])
                stem_idx = int(line[2])
                intervals.append([stem_idx, start_t, end_t])

        melody_sequence = make_blank_melody_sequence(mtrack.duration, fs, hop)

        for interval in intervals:
            stem = mtrack.stems[interval[0]]
            start_t = interval[1]
            end_t = interval[2]

            f0_annotation = stem.pitch_annotation

            if f0_annotation is not None:
                melody_sequence = add_sequence_to_melody(
                    mtrack.duration, f0_annotation, melody_sequence, fs, hop,
                    start_t=start_t, end_t=end_t
                )
            else:
                print("Warning: stem %s has no annotation" % interval[0])

        melody2 = melody_sequence

    else:
        melody2 = None

    return melody2


def create_melody3_annotation(mtrack, fs=FS, hop=HOP):
    """Create a melody3 annotation from pitch annotations

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    fs : float
        Sample rate (samples/second)
    hop : float
        Hop size (samples)

    Returns
    -------
    melody3 : np.array or None
        Melody 3 annotation if a rankings file exists, else None

    """
    melody_rankings = mtrack.melody_rankings

    if melody_rankings != {}:
        inverse_rankings = dict((v, k) for k, v in melody_rankings.items())

        melody_sequence = make_blank_melody_sequence(mtrack.duration, fs, hop)
        dim = 1
        first = True
        for k in sorted(inverse_rankings.keys()):
            if not first:
                n, m = melody_sequence.shape
                temp_mel = np.zeros((n, m + 1))
                temp_mel[:, :-1] = melody_sequence
                melody_sequence = temp_mel
                dim += 1
            first = False
            stem = mtrack.stems[inverse_rankings[k]]
            f0_annotation = stem.pitch_annotation
            melody_sequence = add_sequence_to_melody(
                mtrack.duration, f0_annotation, melody_sequence,
                fs, hop, dim=dim
            )

        melody3 = melody_sequence
    else:
        melody3 = None

    return melody3


def write_melodies_to_csv(mtrack, melody1, melody2, melody3):
    """Write melodies to csv files in the correct directory.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    melody1 : np.array
        Melody 1 annotation
    melody2 : np.array
        Melody 2 annotation
    melody3 : np.array
        Melody 3 annotation

    """

    if melody1 is not None:
        print("writing melody 1...")
        with open(mtrack.melody1_fpath, "w") as fhandle:
            writer = csv.writer(fhandle)
            writer.writerows(melody1)
    else:
        print("melody 1 empty")

    if melody2 is not None:
        print("writing melody 2...")
        with open(mtrack.melody2_fpath, "w") as fhandle:
            writer = csv.writer(fhandle)
            writer.writerows(melody2)
    else:
        print("melody 2 empty")

    if melody3 is not None:
        print("writing melody 3...")
        with open(mtrack.melody3_fpath, "w") as fhandle:
            writer = csv.writer(fhandle)
            writer.writerows(melody3)
    else:
        print("melody 3 empty")


def main(args):
    """Main function to create melody annotations for a multitrack.
    """
    mtrack = medleydb.MultiTrack(args.track_id)
    melody1 = create_melody1_annotation(mtrack)
    melody2 = create_melody2_annotation(mtrack)
    melody3 = create_melody3_annotation(mtrack)
    if args.write_output:
        write_melodies_to_csv(mtrack, melody1, melody2, melody3)


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
