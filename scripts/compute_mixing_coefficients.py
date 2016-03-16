
import argparse
import numpy as np
import os
import scipy.io.wavfile as wavfile
import yaml

import medleydb as mdb


def flatten(w):
    return w.T.ravel()


def loadflat(filename):

    _, w = wavfile.read(filename)
    w = flatten(w)
    return w


def analyze_mix(mtrack):

    mixfile = mtrack.mix_path
    mix_audio = loadflat(mixfile)

    stems = mtrack.stems
    stem_indices = list(stems.keys())
    stem_files = [stems[k].file_path for k in stem_indices]
    stem_audio = np.vstack(
        [loadflat(_) for _ in stem_files]
    )

    coefs, _, _, _ = np.linalg.lstsq(stem_audio.T, mix_audio.T)

    mixing_coeffs = {
        os.path.basename(f): float(c) for f, c in zip(stem_files, coefs)
    }
    return mixing_coeffs


def main(args):
    mtracks = mdb.load_all_multitracks()
    mix_coefs = dict()
    for mtrack in mtracks:
        mix_coefs[os.path.basename(mtrack.mix_path)] = analyze_mix(mtrack)
    with open(args.output_path, 'w') as fdesc:
        yaml.dump(mix_coefs, fdesc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creat ground truth seed files from medleydb")
    parser.add_argument("output_path",
                        type=str,
                        help="Path to save mixing coefficients file.")
    main(parser.parse_args())
