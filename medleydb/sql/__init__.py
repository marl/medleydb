import os
import yaml
import medleydb
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc

from . import model

__all__ = ["session", "from_medleydb", "model"]


def session(filename=None, ephemeral=False, raising=True):
    """Initialize SQLAlchemy session using models and, if possible, existing
    database

    Parameters
    ----------
    filename : string
        Filename of existing or new database. Defaults to :code:`database.sql`
        in your MedleyDB installation
    ephemeral : boolean
        Creates database in RAM only when set to :code:`True`
    raising : boolean
        Raise exception when file does not exist

    Returns
    -------
    session : SQLAlchemy session
        The session

    """
    if filename is None:
        filename = os.path.join(os.environ['MEDLEYDB_PATH'], "database.sql")

    if ephemeral:
        engine = create_engine('sqlite://')
    else:
        if raising and not os.path.isfile(filename):
            raise RuntimeError(
                "%s does not exist, please run medleydb-export first"
                % filename
            )
        engine = create_engine('sqlite:///%s' % filename)

    model.metadata.bind = engine
    model.metadata.create_all()
    Session = sessionmaker(bind=engine)
    _session = Session()

    return _session


def from_medleydb(_session, limit=None):
    """Import data from medleydb

    Parameters
    ----------
    session : SQLAlchemy session
        The session

    """
    import itertools

    with open(medleydb.INST_TAXONOMY) as f_handle:
        data = yaml.load(f_handle)
        walk_taxonomy(data, _session)
        _session.commit()

    if limit is None:
        entries = medleydb.load_all_multitracks()
    else:
        entries = itertools.islice(medleydb.load_all_multitracks(), limit)

    for mt in entries:
        data = model.Track.from_medleydb(mt, _session)
        _session.add(data)

    _session.commit()


def walk_taxonomy(node, session, taxon=None):
    """Recursively walk medleydb taxonomy and create SQLalchemy entries.

    Parameters
    ----------
    nose : collection
        Dict or List containing additional children or leaves
    session : SQLAlchemy session
        The session
    taxon : model.Taxon instance
        The parent taxon to add the following entries to. Optional.

    """
    if isinstance(node, dict):
        for key, item in list(node.items()):
            root = model.Taxon(name=key, parent=taxon)
            walk_taxonomy(item, session, root)
            session.add(root)
    elif isinstance(node, list):
        for item in node:
            instrument = model.Instrument(name=item, taxon=taxon)
            session.add(instrument)


def export(inargs=None, limit=None):
    """CLI program for generating SQLite databases from existing medleydb
    catalogue.

    Parameters
    ----------
    inargs : array
        Arguments passed from CLI
    limit : int
        Limit number of entries being imported. Mainly for unittesting.

    """
    import argparse
    import warnings
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs='?')
    args = parser.parse_args(inargs)

    if args.output is None:
        args.output = os.path.join(os.environ['MEDLEYDB_PATH'], "database.sql")

    try:
        os.remove(args.output)
    except OSError:
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=exc.SAWarning)
        _session = session(args.output, raising=False)
        from_medleydb(_session, limit=limit)
