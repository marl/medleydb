from __future__ import print_function
import medleydb.sql as m
from sqlalchemy.orm import aliased

# These examples assume you have already created `database.sql` using
#
#     $ medleydb-export database.sql
#

session = m.session("database.sql")


print(m.__version__)

# Get all tracks
print(
    session.query(m.model.Track).all()
)


# Get all instrumental tracks
print(
    session.query(m.model.Track).filter(
        m.model.Track.instrumental
    ).all()
)


# Get all instrumental tracks with bleed
print(
    session.query(m.model.Track).filter(
        m.model.Track.instrumental,
        m.model.Track.has_bleed
    ).all()
)


# Get all stems of one track
print(
    session.query(m.model.Track).first().stems
)


# Get all raws of first stem of one track
print(
    session.query(m.model.Track).first().stems[0].raws
)


# Get mix audio of one track
print(
    session.query(m.model.Track).first().data
)


# Get audio from raws of first stem of one track
print(
    session.query(m.model.Track).first().stems[0].raws[0].data
)


# Get first melody of one track
print(
    session.query(m.model.Track).first().melodies[0].data
)


# Get path of all stems and raws of one track, using simple for loops
for stem in session.query(m.model.Track).first().stems:
    print(stem.path)
    for raw in stem.raws:
        print(raw.path)


# Get all tracks containing of at least one tack piano
# We need to join both Stem and Instrument as Instrument is related to Stem,
# which in turn is related to our Track.
print(
    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument
    ).
    filter(
        m.model.Instrument.name == "tack piano"
    ).all()
)


# Get all tracks containing of at least one tack piano
# We need to join Stem, Instrument and Rank. See above for explanation.
print(
    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument,
        m.model.Rank
    ).
    filter(
        m.model.Rank.name == "struck"
    ).all()
)


# Get all tracks containing of at least one string instrument
# We need to join Stem, Instrument and Rank. See above for explanation.
# Additionally we need to join Rank **twice** due to the nested nature of
# the taxonomy.

# TODO: Enable filtering of any layer of the taxonomy.
print(
    session.query(m.model.Track).join(
        m.model.Stem,
        m.model.Instrument,
        m.model.Rank,
    ).
    join(
        "parent",
        aliased=True,
        from_joinpoint=True
    ).
    filter(
        m.model.Rank.name == "strings"
    ).all()
)
