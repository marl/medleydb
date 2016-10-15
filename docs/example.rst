.. _example:

Basic Usage
===========

.. code-block:: python
    :linenos:

    import medleydb as mdb

    # Load all multitracks
    mtrack_generator = mdb.load_all_mulitracks()
    for mtrack in mtrack_generator:
        print(mtrack.track_id)
        # do stuff

    # Load specific multitracks
    mtrack1 = mdb.MultiTrack('LizNelson_Rainfall')
    mtrack2 = mdb.MultiTrack('Phoenix_ScotchMorris')

    # Look at some attributes
    mtrack1.has_bleed
    > False
    mtrack2.has_bleed
    > True
    mtrack1.artist
    > LizNelson
    mtrack2.artist
    > Phoenix
    mtrack1.is_instrumental
    > False
    mtrack2.is_instrumental
    > True
    mtrack1.stem_instruments
    > ['acoustic guitar',
       'clean electric guitar',
       'female singer',
       'female singer',
       'female singer']
    mtrack1.melody1_annotation[:2]
    > [[0.0, 0.0], [0.005804988662131519, 0.0]]

    # Attributes of a stem
    example_stem = mtrack1.stems[1]
    example_stem.instrument
    > 'female singer'
    example_stem.f0_type
    > 'm'
    example_stem.pitch_annotation[:2]
    > [[14.622766439, 167.49], [14.628571428, 166.969]]
    example_stem.component
    > 'melody'

Loading a subset of the dataset
===============================

.. code-block:: python
    :linenos:

    import medleydb as mdb
    track_ids = ['MusicDelta_Rock', 'MusicDelta_Reggae', 'MusicDelta_Disco']
    dataset_subset = mdb.load_multitracks(track_ids)

Getting stems matching an instrument label
==========================================

.. code-block:: python
    :linenos:

    import medleydb as mdb

    dataset = mdb.load_all_multitracks()
    clarinet_files = mdb.get_files_for_instrument('clarinet')

    # get all valid instrument labels
    instruments = mdb.get_valid_instrument_labels()
    print instruments
