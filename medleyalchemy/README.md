MedleyDB SQLAlchemy
===================

This is a simple module for interfacing with MedleyDB catalogs using SQLAlchemy.

The current database of choice is SQLite, additional DB systems may follow.

Usage
-----

### CLI interface.

You can export your medleydb catalog using the commandline utility

    medleydb-export database.sql

This will create a file `database.sql` containing all your medleydb data. 
The process may take a minute or two. All usual medleydb requirements apply
(mainly the `MEDLEYDB_PATH` environment variable).


### SQLAlchemy session 

You can create an SQLAlchemy session and run queries using the following example:

    import medleyalchemy as m

    session = m.session("database.sql")
    session.query(m.model.Track).all()

You can also create a new database using

    import medleyalchemy as m

    session = m.session()
    m.from_medleydb(session)

After a minute or two `session` will have a fully populated database.

Also check `examples/example.py` for a few useful examples how to use the 
SQLAlchemy API.


Requirements
------------

Requirements should be installed automatically during `pip install -e .`:

 - `sqlalchemy`
 - `medleydb-export` and `m.from_medleydb(session)` require `medleydb`


### Testing

 1. Install this module using `pip install -e .[tests]`
 2. Run `medleydb-export database.sql`
 3. Run `py.test`
