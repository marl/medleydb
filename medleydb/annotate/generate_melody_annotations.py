"""Script to generate melody annotations from pitch annotations files"""
import argparse
import os
import csv
import numpy as np

import medleydb
from medleydb.multitrack import _INTERVAL_FMT

HOP = 256.0  # samples
FS = 44100.0  # samples/second


def get_time_stamps(total_duration):
    time_stamps = []
    n_stamps = int(np.ceil((total_duration*FS)/HOP))
    time_stamps = np.array(range(n_stamps))*(HOP/FS)
    return time_stamps


def make_blank_melody_sequence(total_duration):
    time_stamps = get_time_stamps(total_duration)
    melody_sequence = np.zeros((len(time_stamps), 2))
    for i, time_stamp in enumerate(time_stamps):
        melody_sequence[i][0] = time_stamp
    return melody_sequence


def sec_to_idx(time_in_seconds, fs=FS, hop=HOP):
    return int(np.round(time_in_seconds*fs/hop))


def add_sequence_to_melody(total_duration, f0_sequence, melody_sequence, dim=1,
                           start_t=0, end_t=-1):
    if start_t < 0:
        start_t = 0
    if end_t > total_duration:
        end_t = total_duration

    start_idx = sec_to_idx(start_t)
    if end_t == -1:
        end_idx = sec_to_idx(total_duration)
    else:
        end_idx = sec_to_idx(end_t)

    if f0_sequence:
        for time_freq in f0_sequence:
            time = time_freq[0]
            freq = time_freq[1]
            time_idx = sec_to_idx(time)
            if time_idx >= start_idx and time_idx < end_idx:
                melody_sequence[time_idx][dim] = freq

    return melody_sequence


def create_melody1_annotation(mtrack):

    predominant_stem = mtrack.predominant_stem

    if predominant_stem is not None:
        f0_annotation = predominant_stem.get_pitch_annotation()

        melody_sequence = make_blank_melody_sequence(mtrack.duration)
        melody1 = add_sequence_to_melody(
            mtrack.duration, f0_annotation, melody_sequence
        )
    else:
        melody1 = None

    return melody1


def create_melody2_annotation(mtrack):

    intervals_file = os.path.join(
        mtrack._annotation_dir, _INTERVAL_FMT % mtrack.track_id
    )

    if os.path.exists(intervals_file):

        intervals = []
        with open(intervals_file, 'rU') as fhandle:
            linereader = csv.reader(fhandle, delimiter='\t')

            for line in linereader:
                start_t = float(line[0])
                end_t = float(line[1])
                stem_idx = int(line[2])
                intervals.append([stem_idx, start_t, end_t])

        melody_sequence = make_blank_melody_sequence(mtrack.duration)

        for interval in intervals:
            stem = mtrack.get_stem(interval[0])
            start_t = interval[1]
            end_t = interval[2]

            f0_annotation = stem.get_pitch_annotation()

            if f0_annotation is not None:
                melody_sequence = add_sequence_to_melody(
                    mtrack.duration, f0_annotation, melody_sequence,
                    start_t=start_t, end_t=end_t
                )
            else:
                print "Warning: stem %s has no annotation" % interval[0]

        melody2 = melody_sequence

    else:
        melody2 = None

    return melody2


def create_melody3_annotation(mtrack):

    melody_rankings = mtrack.melody_rankings

    if melody_rankings is not None:
        inverse_rankings = dict((v, k) for k, v in melody_rankings.iteritems())

        melody_sequence = make_blank_melody_sequence(mtrack.duration)
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
            stem = mtrack.get_stem(inverse_rankings[k])
            f0_annotation = stem.get_pitch_annotation()
            melody_sequence = add_sequence_to_melody(
                mtrack.duration, f0_annotation, melody_sequence, dim
            )

        melody3 = melody_sequence
    else:
        melody3 = None

    return melody3


def write_melodies_to_csv(mtrack, melody1, melody2, melody3):

    melody1_fname = "%s_MELODY1.csv" % mtrack.track_id
    melody2_fname = "%s_MELODY2.csv" % mtrack.track_id
    melody3_fname = "%s_MELODY3.csv" % mtrack.track_id

    melody1_fpath = os.path.join(mtrack._annotation_dir, melody1_fname)
    melody2_fpath = os.path.join(mtrack._annotation_dir, melody2_fname)
    melody3_fpath = os.path.join(mtrack._annotation_dir, melody3_fname)

    if melody1 is not None:
        print "writing melody 1..."
        with open(melody1_fpath, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(melody1)
    else:
        print "melody 1 empty"

    if melody2 is not None:
        print "writing melody 2..."
        with open(melody2_fpath, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(melody2)
    else:
        print "melody 2 empty"

    if melody3 is not None:
        print "writing melody 3..."
        with open(melody3_fpath, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(melody3)
    else:
        print "melody 3 empty"


def main(args):
    mtrack = medleydb.MultiTrack(args.track_id)
    melody1 = create_melody1_annotation(mtrack)
    melody2 = create_melody2_annotation(mtrack)
    melody3 = create_melody3_annotation(mtrack)
    write_melodies_to_csv(mtrack, melody1, melody2, melody3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("track_id",
                        type=str,
                        help="MedleyDB track id. Ex. MusicDelta_Rock")

    main(parser.parse_args())
