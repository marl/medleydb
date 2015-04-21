import yaml
from . import model
from version import __version__
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc

__all__ = ["session", "from_medleydb", "model", "__version__"]


def session(filename=None):
    """Initialize SQLAlchemy session using models and, if possible, existing
    database

    Parameters
    ----------
    filename : string
        Filename of existing or new database

    Returns
    -------
    session : SQLAlchemy session
        The session

    """
    if filename is None:
        engine = create_engine('sqlite://')
    else:
        engine = create_engine('sqlite:///%s' % filename)

    model.metadata.bind = engine
    model.metadata.create_all()
    Session = sessionmaker(bind=engine)
    _session = Session()

    return _session


def from_medleydb(_session):
    """Import data from medleydb

    Parameters
    ----------
    session : SQLAlchemy session
        The session

    """
    from medleydb import load_all_multitracks, INST_TAXONOMY

    with open(INST_TAXONOMY) as f_handle:
        data = yaml.load(f_handle)
        walk_taxonomy(data, _session)
        _session.commit()

    for mt in load_all_multitracks():
        data = model.Track.from_medleydb(mt, _session)
        _session.add(data)

    _session.commit()


def walk_taxonomy(node, session, rank=None):
    """Recursively walk medleydb taxonomy and create SQLalchemy entries.

    Parameters
    ----------
    nose : collection
        Dict or List containing additional children or leaves
    session : SQLAlchemy session
        The session
    rank : model.Rank instance
        The parent rank to add the following entries to. Optional.

    """
    if isinstance(node, dict):
        for key, item in list(node.items()):
            root = model.Rank(name=key, parent=rank)
            walk_taxonomy(item, session, root)
            session.add(root)
    elif isinstance(node, list):
        for item in node:
            instrument = model.Instrument(name=item, rank=rank)
            session.add(instrument)


def export(inargs=None):
    """CLI program for generating SQLite databases from existing medleydb
    catalogue.

    Parameters
    ----------
    inargs : array
        Arguments passed from CLI

    """
    import argparse
    import warnings
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    args = parser.parse_args(inargs)

    try:
        os.remove(args.output)
    except OSError:
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=exc.SAWarning)
        _session = session(args.output)
        from_medleydb(_session)
