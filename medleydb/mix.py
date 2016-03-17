"""Functions for creating new mixes from medleydb multitracks.
"""
import shutil

from . import sox


def mix_multitrack(mtrack, output_path, stem_indices=None,
                   alternate_weights=None, alternate_files=None,
                   additional_files=None):
    """
    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output wav file.
    stem_indices : list
        stem indices to include in mix.
        If None, mixes all stems
    alternate_weights : dict
        Dictionary with stem indices as keys and mixing coefficients as values.
        Stem indices present that are not in this dictionary will use the
        default estimated mixing coefficient.
    alternate_files : dict
        Dictionary with stem indices as keys and filepaths as values.
        Audio file to use in place of original stem. Stem indices present that
        are not in this dictionary will use the original stems.
    additional_files : list of tuple
        List of tuples of (filepath, mixing_coefficient) pairs to additionally
        add to final mix.
    """
    if stem_indices is None:
        stem_indices = list(mtrack.stems.keys())

    if alternate_files is None:
        alternate_files = {}
    alternate_files_idx = list(alternate_files.keys())

    if alternate_weights is None:
        alternate_weights = {}
    alternate_weights_idx = list(alternate_weights.keys())

    weights = []
    filepaths = []
    for index in stem_indices:
        if index in alternate_files_idx:
            filepaths.append(alternate_files[index])
        else:
            filepaths.append(mtrack.stems[index].file_path)

        if index in alternate_weights_idx:
            weights.append(alternate_weights[index])
        else:
            weights.append(mtrack.stems[index].mixing_coefficient)

    if additional_files is not None:
        for f, w in additional_files:
            filepaths.append(f)
            weights.append(w)

    if len(filepaths) == 1:
        shutil.copyfile(filepaths[0], output_path)
    else:
        sox.mix_weighted(filepaths, weights, output_path)


def mix_melody_stems(mtrack, output_path, max_melody_stems=None,
                     include_percussion=False, require_mono=False):
    if max_melody_stems is None:
        max_melody_stems = 100

    melody_rankings = mtrack.melody_rankings
    inverse_ranking = {v: k for k, v in melody_rankings.items()}
    n_melody_stems = len(list(melody_rankings.keys()))
    stem_indices = []
    melody_indices = []
    n_chosen = 0
    for i in range(1, n_melody_stems + 1):
        if n_chosen >= max_melody_stems:
            break

        this_stem_index = inverse_ranking[i]
        if require_mono:
            if mtrack.stems[this_stem_index].f0_type == 'm':
                stem_indices.append(this_stem_index)
                melody_indices.append(this_stem_index)
                n_chosen += 1
        else:
            stem_indices.append(this_stem_index)
            melody_indices.append(this_stem_index)
            n_chosen += 1

    if include_percussion:
        percussive_indices = [
            i for i, s in mtrack.stems.items() if s.f0_type == 'u'
        ]

        for i in percussive_indices:
            stem_indices.append(i)

    mix_multitrack(mtrack, output_path, stem_indices=stem_indices)
    return melody_indices


def mix_mono_stems(mtrack, output_path, include_percussion=False):
    stems = mtrack.stems
    stem_indices = []
    mono_indices = []
    for i in stems.keys():
        if stems[i].f0_type == 'm':
            stem_indices.append(i)
            mono_indices.append(i)
        elif include_percussion and stems[i].f0_type == 'u':
            stem_indices.append(i)

    mix_multitrack(mtrack, output_path, stem_indices=stem_indices)
    return mono_indices
