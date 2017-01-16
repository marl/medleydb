"""Generate activation confidence annotations.
"""
from __future__ import division
import scipy.signal
import numpy as np
import librosa
import medleydb
import os
import argparse


def compute_activation_confidence(mtrack, win_len=4096, lpf_cutoff=0.075,
                                 theta=0.15, var_lambda=20.0,
                                 amplitude_threshold=0.01):
    """Create the activation confidence annotation for a multitrack. The final
    activation matrix is computed as:
        `C[i, t] = 1 - (1 / (1 + e**(var_lambda * (H[i, t] - theta))))`
    where H[i, t] is the energy of stem `i` at time `t`

    Parameters
    ----------
    mtrack : MultiTrack
        Multitrack object
    win_len : int, default=4096
        Number of samples in each window
    lpf_cutoff : float, default=0.075
        Lowpass frequency cutoff fraction
    theta : float
        Controls the threshold of activation.
    var_labmda : float
        Controls the slope of the threshold function.
    amplitude_threshold : float
        Energies below this value are set to 0.0

    Returns
    -------
    C : np.array
        Array of activation confidence values shape (n_conf, n_stems)
    stem_index_list : list
        List of stem indices in the order they appear in C

    """
    H = []
    stem_index_list = []

    # MATLAB equivalent to @hanning(win_len)
    win = scipy.signal.windows.hann(win_len + 2)[1:-1]

    for stem_idx, track in mtrack.stems.items():
        audio, rate = librosa.load(track.audio_path, sr=44100, mono=True)
        H.append(track_energy(audio.T, win_len, win))
        stem_index_list.append(stem_idx)

    # list to numpy array
    H = np.array(H)

    # normalization (to overall energy and # of sources)
    E0 = np.sum(H, axis=0)
    
    H = len(mtrack.stems) * H / np.max(E0)
    # binary thresholding for low overall energy events
    H[:, E0 < amplitude_threshold] = 0.0

    # LP filter
    b, a = scipy.signal.butter(2, lpf_cutoff, 'low')
    H = scipy.signal.filtfilt(b, a, H, axis=1)

    # logistic function to semi-binarize the output; confidence value
    C = 1.0 - (1.0 / (1.0 + np.exp(np.dot(var_lambda, (H - theta)))))

    # add time column
    time = librosa.core.frames_to_time(
        np.arange(C.shape[1]), sr=rate, hop_length=win_len // 2
    )

    # stack time column to matrix
    C_out = np.vstack((time, C))
    return C_out.T, stem_index_list


def track_energy(wave, win_len, win):
    """Compute the energy of an audio signal

    Parameters
    ----------
    wave : np.array
        The signal from which to compute energy
    win_len: int
        The number of samples to use in energy computation
    win : np.array
        The windowing function to use in energy computation

    Returns
    -------
    energy : np.array
        Array of track energy

    """
    hop_len = win_len // 2

    wave = np.lib.pad(
        wave, pad_width=(win_len-hop_len, 0), mode='constant', constant_values=0
    )

    # post padding
    wave = librosa.util.fix_length(
        wave, int(win_len * np.ceil(len(wave) / win_len))
    )

    # cut into frames
    wavmat = librosa.util.frame(wave, frame_length=win_len, hop_length=hop_len)

    # Envelope follower
    wavmat = hwr(wavmat) ** 0.5  # half-wave rectification + compression

    return np.mean((wavmat.T * win), axis=1)


def hwr(x):
    """ Half-wave rectification.

    Parameters
    ----------
    x : array-like
        Array to half-wave rectify

    Returns
    -------
    x_hwr : array-like
        Half-wave rectified array

    """
    return (x + np.abs(x)) / 2


def write_activations_to_csv(mtrack, activations, stem_index_list,
                             overwrite_existing=False):
    """Write computed activations to the multitrack's activation confidence
    file.

    Parameters
    ----------
    mtrack : MultiTrack
        Multitrack object
    activations : np.array
        Matrix of stem activations
    stem_index_list : list
        List of stem indices
    overwrite_existing : bool, default=False
        If True, overwrites an existing activation confidence file

    """
    stem_str = ",".join(
        ["S%02d" % stem_idx for stem_idx in stem_index_list]
    )
    if not os.path.exists(mtrack.activation_conf_fpath) or overwrite_existing:
        np.savetxt(
            mtrack.activation_conf_fpath,
            activations,
            header='time,{}'.format(stem_str),
            delimiter=',',
            fmt='%.4f',
            comments=''
        )


def main(args):
    """Main function. Computes the activation confidence annotation for a given
    multitrack id.
    """
    mtrack = medleydb.MultiTrack(args.track_id)
    if os.path.exists(mtrack.activation_conf_fpath):
        return True

    activations, index_list = compute_activation_confidence(mtrack)
    write_activations_to_csv(mtrack, activations, index_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("track_id",
                        type=str,
                        default="LizNelson_Rainfall",
                        help="MedleyDB track id. Ex. LizNelson_Rainfall")
    main(parser.parse_args())
