
import argparse
import numpy as np
import scipy.io.wavfile as wavfile
import scipy.optimize
import scipy.optimize.nnls as nnls
from scipy.optimize import minimize
from scipy.optimize import leastsq
from scipy.optimize import curve_fit
import scipy.fftpack as fft
import librosa
import yaml

import medleydb as mdb


def get_feature(filename):
    sr = 8192
    nfft = 8192
    y, fs = librosa.load(filename, mono=True, sr=sr)
    feature = np.abs(librosa.stft(y, n_fft=nfft, hop_length=nfft, win_length=nfft))
    return feature


def linear_model(x, A, y):
    return np.linalg.norm(np.dot(A, x) - y, ord=2)


def analyze_mix(mtrack):

    mixfile = mtrack.mix_path
    mix_audio = get_feature(mixfile)

    stems = mtrack.stems
    stem_indices = list(stems.keys())
    stem_files = [stems[k].audio_path for k in stem_indices]
    stem_audio = np.array(
        [get_feature(_) for _ in stem_files]
    )
    print(stem_audio.shape)
    # coefs, _ = nnls(stem_audio.T, mix_audio.T)

    bounds = tuple([(0.5, 2) for _ in range(len(stem_indices))])
    res = minimize(
        linear_model, x0=np.ones((len(stem_indices), )), args=(stem_audio.T, mix_audio.T),
        bounds=bounds
    )
    print(res)
    coefs = res['x']

    mixing_coeffs = {
        int(i): float(c) for i, c in zip(stem_indices, coefs)
    }
    return mixing_coeffs


def main(args):
    mtracks = mdb.load_all_multitracks(dataset_version=['V1', 'V2', 'EXTRA', 'BACH10'])
    # mtracks = [mdb.MultiTrack("MusicDelta_Rock"), mdb.MultiTrack("Aha_TakeOnMe")]
    mix_coefs = dict()
    for mtrack in mtracks:
        print(mtrack.track_id)
        mix_coefs[mtrack.track_id] = analyze_mix(mtrack)
        print(mix_coefs[mtrack.track_id])
        print("")
        with open(args.output_path, 'w') as fdesc:
            yaml.dump(mix_coefs, fdesc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Estimate multitrack mixing coefficients")
    parser.add_argument("output_path",
                        type=str,
                        help="Path to save mixing coefficients file.")
    main(parser.parse_args())
