"""
fill_tony_file.py

Fill in missing time frames in a Tony file, write the output to file.

Created by Rachel Bittner <rmb456@nyu.edu>
and Justin Salamon <justin.salamon@nyu.edu>

This code is released as part of the MedleyDB library for working
with the MedleyDB dataset: http://marl.smusic.nyu.edu/medleydb. 

This code is a component of the work presented in the following publication:

R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello,
"MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in
15th International Society for Music Information Retrieval Conference,
Taipei, Taiwan, Oct. 2014.
"""

import os
import numpy as np
import csv
import argparse

HOP = 256.0 #Tony default hop size
FS = 44100.0 #Tony default output sample rate


def fill_f0_track(tony_csv_file, output_file_path, total_duration):
    """ Fill in missing time frames in a Tony file, write the output to file.
    Params:
        - tony_csv_file: path to tony ouputted csv file
        - output_file_path: path to save location of filled in file
        - total_duration: length (in seconds) of the annotation audiofile
    """
    tony_f0 = read_tony_file(tony_csv_file)

    if not tony_f0:
        return False

    if tony_f0:
        start_idx = sec_to_idx(0)
        end_idx = sec_to_idx(total_duration)
        f0_sequence = make_blank_f0_sequence(total_duration)
        for time_freq in tony_f0:
            time = time_freq[0]
            freq = time_freq[1]
            time_idx = sec_to_idx(time)
            if time_idx >= start_idx and time_idx < end_idx:
                f0_sequence[time_idx][1] = freq
    
    result = write_f0_to_csv(f0_sequence, output_file_path)
    if result:
        return True
    else:
        return False


def read_tony_file(fpath):
    """ Read a Tony csv file.
    """
    if os.path.exists(fpath):
        data_lines = [line.strip() for line in open(fpath)]
        tony_f0 = []
        for line in data_lines:
            time, f_0 = line.split(',')[0:2]
            tony_f0.append([float(time), float(f_0)])
        return tony_f0
    else:
        return False


def get_time_stamps(total_duration):
    """ Get a list of evenly spaced time stamps based on Tony's parameters.
    Params:
        - total_duration: length (in seconds) of the annotation audiofile
    """
    time_stamps = []
    n_stamps = int(np.ceil((total_duration*FS)/HOP))
    time_stamps = np.array(range(n_stamps))*(HOP/FS)
    return time_stamps


def make_blank_f0_sequence(total_duration):
    """ Make a complete f0 sequence filled with 0's.
        First column is time, second column is frequency.
    """
    time_stamps = get_time_stamps(total_duration)
    f0_sequence = np.zeros((len(time_stamps), 2))
    for i, time_stamp in enumerate(time_stamps):
        f0_sequence[i][0] = time_stamp
    return f0_sequence


def sec_to_idx(time_in_seconds, fs=FS, hop=HOP):
    """ Get the index of a given time stamps
    """
    return int(np.round(time_in_seconds*fs/hop))


def write_f0_to_csv(f0_sequence, output_file_path):
    """ Write f0 sequence to a csv file.
    """
    if len(f0_sequence):
        with open(output_file_path, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(f0_sequence)
        return True
    else:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill in missing time frames in a Tony file, write the output to file.")
    parser.add_argument("tonyfile", help="path to tony ouput csv file")
    parser.add_argument("outputfile", help="path to save location of filled in file")
    parser.add_argument("duration", help="length (in seconds) of the annotation audiofile")

    args = parser.parse_args()

    fill_f0_track(args.tonyfile, args.outputfile, float(args.duration))
