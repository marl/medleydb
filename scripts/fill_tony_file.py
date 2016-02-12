#!/usr/bin/env python
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

HOP = 256.0  # Tony default hop size
FS = 44100.0  # Tony default output sample rate


def read_tony_file(fpath):
    """Read a tony-generated csv file.

    Parameters
    ----------
    fpath : str
        Path to tony-generated csv file.

    Returns
    -------
    tony_f0 : array
        Array of tony-generated f0 values and corresponding time stamps.
    """

    assert os.path.exists(fpath), "File path does not exist."

    with open(fpath) as f_handle:
        tony_f0 = []
        linereader = csv.reader(f_handle)
        for line in linereader:
            tony_f0.append([float(val) for val in line[:2]])
    return tony_f0


def get_time_stamps(total_duration):
    """Get a list of evenly spaced time stamps based on Tony's parameters.

    Parameters
    ----------
    total_duration : float
        Length (in seconds) of annotation's corresponding audio file.

    Returns
    -------
    time_stamps : array
        Array of evenly spaced time stamps spanning the entire annotation.
    """
    n_stamps = int(np.ceil((total_duration*FS)/HOP))
    return np.arange(n_stamps)*(HOP/FS)


def make_blank_f0_sequence(total_duration):
    """Make a complete f0 sequence filled with 0's.
    First column is time, second column is frequency.

    Parameters
    ----------
    total_duration : float
        Length (in seconds) of annotation's corresponding audio file.

    Returns
    -------
    f0_sequence : array
        Array of filled in f0 values and corresponding time stamps.
    """
    time_stamps = get_time_stamps(total_duration)
    f0_sequence = np.zeros((len(time_stamps), 2))
    f0_sequence[:, 0] = time_stamps
    return f0_sequence


def sec_to_idx(time_in_seconds, sample_rate=FS, hop=HOP):
    """Compute the array index of a given time stamp.

    Parameters
    ----------
    time_in_seconds : float
        Time stamp, in seconds.
    sample_rate : float
        Annotation sample rate.
    hop : float
        Annotation hop size.

    Returns
    -------
    array_idx : int
        Index of time stamp in filled f0 array.
    """
    return int(np.round(time_in_seconds*sample_rate/hop))


def write_f0_to_csv(f0_sequence, output_file_path):
    """Write f0 sequence to a csv file.

    Parameters
    ----------
    f0_sequence : array
        Filled f0 sequence with corresponding time stamps.
    output_file_path : str
        Path to save csv file.
    """
    assert len(f0_sequence) != 0, "f0 sequence is empty."
    with open(output_file_path, "wb") as fpath:
        writer = csv.writer(fpath)
        writer.writerows(f0_sequence)


def main(args):
    """Fill in missing time frames in a Tony file, write the output to file.

    Parameters
    ----------
    tony_csv_file : str
        Path to tony-generated csv file.
    output_file_path : str
        Path to save location of filled-in file.
    duration : float
        Length (in seconds) of the annotation's corresponding audio file.
    """

    tony_f0 = read_tony_file(args.tonyfile)

    assert tony_f0, "Tony file does not exist."

    start_idx = sec_to_idx(0)
    end_idx = sec_to_idx(args.duration)
    f0_sequence = make_blank_f0_sequence(args.duration)
    for time_freq in tony_f0:
        time = time_freq[0]
        freq = time_freq[1]
        time_idx = sec_to_idx(time)
        if time_idx >= start_idx and time_idx < end_idx:
            f0_sequence[time_idx][1] = freq

    write_f0_to_csv(f0_sequence, args.outputfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fill in missing time frames in a Tony file,"
                    "write the output to file.")
    parser.add_argument("tonyfile",
                        type=str,
                        help="Path to tony ouput csv file.")
    parser.add_argument("outputfile",
                        type=str,
                        help="Path to save location of filled in file.")
    parser.add_argument("duration",
                        type=float,
                        help="Length (in seconds) of annotation audio file.")

    main(parser.parse_args())
