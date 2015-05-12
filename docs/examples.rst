Examples
========

SQL Examples
------------

These examples assume you have already created `database.sql` using

.. code:: bash

    $ medleydb-export database.sql



Get all tracks

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).all()


Get all instrumental tracks

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).filter(
        m.model.Track.instrumental
    ).all()


Get all instrumental tracks with bleed

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).filter(
        m.model.Track.instrumental,
        m.model.Track.has_bleed
    ).all()


Get all stems of one track

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).first().stems


Get all raws of first stem of one track

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).first().stems[0].raws


Get mix audio of one track

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).first().audio_data


Get audio from raws of first stem of one track

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).first().stems[0].raws[0].audio_data


Get first melody of one track

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).first().melodies[0].annotation_data


Get path of all stems and raws of one track, using simple for loops

.. code:: python

    import medleydb.sql as m
    session = m.session()

    for stem in session.query(m.model.Track).first().stems:
        stem.audio_path
        for raw in stem.raws:
            raw.audio_path


Get all tracks containing of at least one tack piano
We need to join both Stem and Instrument as Instrument is related to Stem,
which in turn is related to our Track.

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument
    ).filter(
        m.model.Instrument.name == "tack piano"
    ).all()


Get all tracks containing of at least one tack piano
We need to join Stem, Instrument and Taxon. See above for explanation.

.. code:: python

    import medleydb.sql as m
    session = m.session()

    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument,
        m.model.Taxon
    ).filter(
        m.model.Taxon.name == "struck"
    ).all()


Get all tracks containing of at least one string instrument
We need to join Stem, Instrument and Taxon. See above for explanation.
Additionally we need to join Taxon **twice** due to the nested nature of
the taxonomy.

TODO: Enable filtering of any layer of the taxonomy.

.. code:: python

    import medleydb.sql as m
    session = m.session()
    from sqlalchemy.orm import aliased

    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument,
        m.model.Taxon,
    ).join(
        "parent",
        aliased=True,
        from_joinpoint=True
    ).filter(
        m.model.Taxon.name == "strings"
    ).all()
