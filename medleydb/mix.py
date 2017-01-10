"""Functions for creating new mixes from medleydb multitracks.
"""
import shutil
import sox


VOCALS = ["male singer", "female singer", "male speaker", "female speaker",
          "male rapper", "female rapper", "beatboxing", "vocalists"]


def mix_multitrack(mtrack, output_path, stem_indices=None,
                   alternate_weights=None, alternate_files=None,
                   additional_files=None):
    """Mix the stems of a multitrack to create a new mix.
    Can optionally adjust the volume of stems and replace, remove, or add
    stems.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output file.
    stem_indices : list or None, default=None
        stem indices to include in mix.
        If None, mixes all stems
    alternate_weights : dict or None, default=None
        Dictionary with stem indices as keys and mixing coefficients as values.
        Stem indices present that are not in this dictionary will use the
        default estimated mixing coefficient.
    alternate_files : dict or None, default=None
        Dictionary with stem indices as keys and filepaths as values.
        Audio file to use in place of original stem. Stem indices present that
        are not in this dictionary will use the original stems.
    additional_files : list of tuple or None, default=None
        List of tuples of (filepath, mixing_coefficient) pairs to additionally
        add to final mix.

    """
    filepaths, weights = _build_mix_args(
        mtrack, stem_indices, alternate_weights, alternate_files,
        additional_files
    )

    if len(filepaths) == 1:
        shutil.copyfile(filepaths[0], output_path)
    else:
        cbn = sox.Combiner()
        cbn.build(
            filepaths, output_path, 'mix', input_volumes=weights
        )


def _build_mix_args(mtrack, stem_indices, alternate_weights, alternate_files,
                    additional_files):
    """Create lists of filepaths and weights to use in final mix.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
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
    additional_files : list of tuples
        List of tuples of (filepath, mixing_coefficient) pairs to additionally
        add to final mix.

    Returns
    -------
    filepaths : list
        List of filepaths that were included in mix.
    weights : list
        List of weights that were used in mix

    """
    if stem_indices is None:
        stem_indices = list(mtrack.stems.keys())

    if alternate_files is None:
        alternate_files = {}

    if alternate_weights is None:
        alternate_weights = {}

    weights = []
    filepaths = []
    for index in stem_indices:
        if index in alternate_files.keys():
            filepaths.append(alternate_files[index])
        else:
            filepaths.append(mtrack.stems[index].audio_path)

        if index in alternate_weights.keys():
            weights.append(alternate_weights[index])
        else:
            weights.append(mtrack.stems[index].mixing_coefficient)

    if additional_files is not None:
        for fpath, weight in additional_files:
            filepaths.append(fpath)
            weights.append(weight)

    return filepaths, weights


def mix_melody_stems(mtrack, output_path, max_melody_stems=None,
                     include_percussion=False, require_mono=False):
    """Creates a mix using only the stems labeled as melody.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output wav file.
    max_melody_stems : int or None, default=None
        The maximum number of melody stems to mix. If None, uses the number of
        melody stems in the mix.
    include_percussion : bool, default=False
        If true, adds percussion stems to the mix.
    require_mono : bool, default=False
        If true, only includes melody stems that are monophonic instruments.

    Returns
    -------
    melody_indices : list
        List of selected melody indices.
    stem_indices : list
        List of stem indices used in mix.

    """
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
    return melody_indices, stem_indices


def mix_mono_stems(mtrack, output_path, include_percussion=False):
    """Creates a mix using only the stems that are monophonic. For example, in
    mix with piano, voice, and clarinet, the resulting mix would include
    only voice and clarinet.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output wav file.
    include_percussion : bool, default=False
        If true, percussive instruments are included in the mix. If false, they
        are excluded.

    Returns
    -------
    mono_indices : list
        List of stem indices containing monophonic instruments.
    stem_indices : list
        List of stem indices used in mix.

    """
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
    return mono_indices, stem_indices


def mix_no_vocals(mtrack, output_path):
    """Remixes a multitrack with anything type of vocals removed.
    If no vocals are present, the mix will be a simple weighted linear remix.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output file.

    Returns
    -------
    stem_indices : list
        List of stem indices used in mix.

    """
    stems = mtrack.stems
    stem_indices = []
    for i in stems.keys():
        if stems[i].instrument not in VOCALS:
            stem_indices.append(i)

    mix_multitrack(mtrack, output_path, stem_indices=stem_indices)
    return stem_indices


def remix_vocals(mtrack, output_path, vocals_scale):
    """Remixes a multitrack, changing the volume of the vocals.

    Parameters
    ----------
    mtrack : Multitrack
        Multitrack object
    output_path : str
        Path to save output wav file.
    vocals_scale : float
        The target scale factor for vocals. A value of 1 keeps the volume the
        same. Values above 1 increase the volume and below 1 decrease it.

    Returns
    -------
    alternate_weights : dict
        Dictionary of vocal weights keyed by vocal stem index.

    """
    stems = mtrack.stems
    alternate_weights = {}
    for i in stems.keys():
        if stems[i].instrument in VOCALS:
            vocal_weight = stems[i].mixing_coefficient * vocals_scale
            alternate_weights[i] = vocal_weight

    mix_multitrack(
        mtrack, output_path, alternate_weights=alternate_weights
    )
    return alternate_weights
