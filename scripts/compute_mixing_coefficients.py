
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


def get_feature_stft(filename):
    sr = 8192
    nfft = 8192
    y, fs = librosa.load(filename, mono=True, sr=sr)
    feature = np.abs(
        librosa.stft(y, n_fft=nfft, hop_length=nfft, win_length=nfft)
    )
    return feature


def get_feature_audio(filename):
    sr = 8192
    y, fs = librosa.load(filename, mono=True, sr=sr)
    feature = y**2.0
    return feature


def linear_model(x, A, y):
    return np.linalg.norm(np.dot(A, x) - y, ord=2)


def analyze_mix_stft(mtrack):
    mixfile = mtrack.mix_path
    mix_audio = get_feature_stft(mixfile)

    stems = mtrack.stems
    stem_indices = list(stems.keys())
    n_stems = len(stem_indices)
    stem_files = [stems[k].audio_path for k in stem_indices]
    stem_audio = np.array(
        [get_feature_stft(_) for _ in stem_files]
    )

    # force weights to be between 0.5 and 4
    bounds = tuple([(0.5, 4.0) for _ in range(n_stems)])
    res = minimize(
        linear_model, x0=np.ones((n_stems, )), args=(stem_audio.T, mix_audio.T),
        bounds=bounds
    )
    coefs = res['x']

    mixing_coeffs = {
        int(i): float(c) for i, c in zip(stem_indices, coefs)
    }
    return mixing_coeffs


def analyze_mix_audio(mtrack):
    mixfile = mtrack.mix_path
    mix_audio = get_feature_audio(mixfile)

    stems = mtrack.stems
    stem_indices = list(stems.keys())
    n_stems = len(stem_indices)
    stem_files = [stems[k].audio_path for k in stem_indices]
    stem_audio = np.array(
        [get_feature_audio(_) for _ in stem_files]
    )

    # force weights to be between 0.5 and 4
    bounds = tuple([(0.5, 4.0) for _ in range(n_stems)])
    res = minimize(
        linear_model, x0=np.ones((n_stems, )), args=(stem_audio.T, mix_audio.T),
        bounds=bounds
    )
    coefs = res['x']

    mixing_coeffs = {
        int(i): float(c) for i, c in zip(stem_indices, coefs)
    }
    return mixing_coeffs


def main(args):
    mtracks = mdb.load_all_multitracks(dataset_version=['V1', 'V2', 'EXTRA', 'BACH10'])
    mix_coefs = dict()
    for mtrack in mtracks:

        print(mtrack.track_id)

        # compute mixing weights on both stft and squared audio
        coeffs_stft = analyze_mix_stft(mtrack)
        coeffs_audio = analyze_mix_audio(mtrack)

        mix_coefs[mtrack.track_id] = {'stft': coeffs_stft, 'audio': coeffs_audio}

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
