import os.path
from sqlalchemy import Table, ForeignKey, Column, MetaData
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship, synonym, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

__all__ = [
    "Rank",
    "Instrument",
    "Track",
    "Stem",
    "Raw",
    "Composer",
    "Producer",
]


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


class Rank(DeclarativeBase):
    """ One entry in the taxonomy. May have one or more ranks or instruments
    as children

    """
    __tablename__ = 'rank'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), unique=True, nullable=False)

    parent_id = Column(Integer, ForeignKey('rank.id'))
    parent = relationship('Rank', backref='children', remote_side=[id])
    instruments = relationship('Instrument', backref='rank')

    def __repr__(self):
        return '<Rank: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Instrument(DeclarativeBase):
    """ An instrument. Always a child of a Rank. Has stems and raws.

    """
    __tablename__ = 'instrument'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), unique=True, nullable=False)

    rank_id = Column(Integer, ForeignKey('rank.id'))
    stems = relationship('Stem', backref='instrument')
    raws = relationship('Raw', backref='instrument')

    @classmethod
    def from_medleydb(cls, instance, session):
        tmp = cls(
            filename=instance.file_path,
            component=instance.component,
        )

        tmp.instrument = Instrument

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Instrument: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Track(DeclarativeBase):
    """ A track. Has stems, melodies, composers and producers.

    """
    __tablename__ = 'track'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), unique=True, nullable=False)
    artist = Column(Unicode(256), nullable=False)
    excerpt = Column(Boolean)
    genre = Column(Unicode(256), nullable=False)
    has_bleed = Column(Boolean)
    instrumental = Column(Boolean)
    data_dir = Column(Unicode(256), unique=True, nullable=False)
    metadata_filename = Column(Unicode(256), unique=True, nullable=False)
    mix_filename = Column(Unicode(256), unique=True, nullable=False)
    origin = Column(Unicode(256), nullable=False)
    raw_dir = Column(Unicode(256), nullable=False)
    stem_dir = Column(Unicode(256), nullable=False)
    website = Column(Unicode(256), nullable=False)
    duration = Column(Integer, nullable=False)

    stems = relationship('Stem', backref='track')
    melodies = relationship('Melody', backref='track')
    composers = association_proxy(
        'track_composer', 'composer',
        creator=lambda composer: TrackComposer(composer=composer)
    )
    producers = association_proxy(
        'track_producer', 'producer',
        creator=lambda producer: TrackProducer(producer=producer)
    )

    @hybrid_property
    def data_path(self):
        return os.path.join(
            os.environ['MEDLEYDB_PATH'],
            self.data_dir,
        )

    @hybrid_property
    def data(self):
        import scipy.io.wavfile
        return scipy.io.wavfile.read(self.mix_path)

    @hybrid_property
    def mix_path(self):
        return os.path.join(
            self.data_path,
            self.mix_filename,
        )

    @hybrid_property
    def metadata_path(self):
        return os.path.join(
            self.data_path,
            self.metadata_filename,
        )

    @classmethod
    def from_medleydb(cls, instance, session):
        import medleydb.multitrack

        tmp = cls(
            artist=instance.artist,
            name=instance.title,
            excerpt=instance.is_excerpt,
            genre=instance.genre,
            has_bleed=instance.has_bleed,
            instrumental=instance.is_instrumental,
            data_dir=os.path.relpath(
                os.path.dirname(instance.mix_path),
                os.environ['MEDLEYDB_PATH']
            ),
            metadata_filename=os.path.basename(instance._meta_path),
            mix_filename=os.path.basename(instance.mix_path),
            origin=instance.origin,
            raw_dir=instance._metadata['raw_dir'],
            stem_dir=instance._metadata['stem_dir'],
            website=str(instance._metadata['website']),
            duration=int(instance.duration),
        )

        with session.no_autoflush:
            for item in instance._metadata['composer']:
                tmp.composers.append(
                    get_or_create(
                        session, Composer, name=item
                    )
                )

            for item in instance._metadata['producer']:
                tmp.producers.append(
                    get_or_create(
                        session, Producer, name=item
                    )
                )

            for key, stem in list(instance._metadata['stems'].items()):
                tmp.stems.append(
                    Stem.from_medleydb(stem, session, name=key)
                )

            for item in (
                medleydb.multitrack._MELODY1_FMT,
                medleydb.multitrack._MELODY2_FMT,
                medleydb.multitrack._MELODY3_FMT
            ):
                tmp.melodies.append(
                    get_or_create(
                        session, Melody, filename=item % instance.track_id
                    )
                )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Track: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Stem(DeclarativeBase):
    """ A stem. Belongs to a track and instrument and has raws.

    """
    __tablename__ = 'stem'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), nullable=False)
    filename = Column(Unicode(256), unique=True, nullable=False)
    component = Column(Unicode(256))

    track_id = Column(Integer, ForeignKey('track.id'))
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    raws = relationship('Raw', backref='stem')

    @hybrid_property
    def path(self):
        return os.path.join(
            self.track.data_path,
            self.track.stem_dir,
            self.filename
        )

    @hybrid_property
    def data(self):
        import scipy.io.wavfile
        return scipy.io.wavfile.read(self.path)

    @classmethod
    def from_medleydb(cls, instance, session, name=''):
        tmp = cls(
            name=name,
            filename=instance['filename'],
            component=instance['component'],
            instrument=get_or_create(
                session, Instrument, name=instance['instrument']
            )
        )

        for key, raw in list(instance['raw'].items()):
            tmp.raws.append(
                Raw.from_medleydb(raw, session, name=key)
            )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Stem: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Raw(DeclarativeBase):
    """ A stem. Belongs to a stem and instrument.

    """
    __tablename__ = 'raw'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), nullable=False)
    filename = Column(Unicode(256), unique=True, nullable=False)

    stem_id = Column(Integer, ForeignKey('stem.id'))
    instrument_id = Column(Integer, ForeignKey('instrument.id'))

    @hybrid_property
    def path(self):
        return os.path.join(
            self.stem.track.data_path,
            self.stem.track.raw_dir,
            self.filename
        )

    @hybrid_property
    def data(self):
        import scipy.io.wavfile
        return scipy.io.wavfile.read(self.path)

    @classmethod
    def from_medleydb(cls, instance, session, name=''):
        tmp = cls(
            name=name,
            filename=instance['filename'],
            instrument=get_or_create(
                session, Instrument, name=instance['instrument']
            )
        )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Raw: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Melody(DeclarativeBase):
    """ A melody. Belongs to a track.

    """
    __tablename__ = 'melody'
    id = Column(Integer, autoincrement=True, primary_key=True)
    filename = Column(Unicode(256), unique=True, nullable=False)

    track_id = Column(Integer, ForeignKey('track.id'))

    @hybrid_property
    def path(self):
        return os.path.join(
            self.track.data_path,
            self.filename
        )

    @hybrid_property
    def data(self):
        import medleydb.multitrack
        return medleydb.multitrack.read_annotation_file(self.path)

    @classmethod
    def from_medleydb(cls, instance, session, name=''):
        tmp = cls(
            name=name,
            filename=instance['filename'],
        )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Melody: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Composer(DeclarativeBase):
    """ A copmoser. Belongs to one or more tracks.

    """
    __tablename__ = 'composer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), unique=True, nullable=False)

    tracks = association_proxy(
        'track_composer', 'track',
        creator=lambda track: TrackComposer(track=track)
    )

    def __repr__(self):
        return '<Composer: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Producer(DeclarativeBase):
    """ A producer. Belongs to one or more tracks.

    """
    __tablename__ = 'producer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(256), unique=True, nullable=False)

    tracks = association_proxy(
        'track_producer', 'track',
        creator=lambda track: TrackProducer(track=track)
    )

    def __repr__(self):
        return '<Producer: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class TrackComposer(DeclarativeBase):
    __tablename__ = 'track_composer'
    track_id = Column(
        'track_fk',
        Integer,
        ForeignKey('track.id'),
        primary_key=True
    )
    composer_id = Column(
        'composer_fk',
        Integer,
        ForeignKey('composer.id'),
        primary_key=True
    )

    track = relationship(Track, backref=backref("track_composer"))
    composer = relationship(Composer, backref=backref("track_composer"))


class TrackProducer(DeclarativeBase):
    __tablename__ = 'track_producer'
    track_id = Column(
        'track_fk',
        Integer,
        ForeignKey('track.id'),
        primary_key=True
    )
    producer_id = Column(
        'producer_fk',
        Integer,
        ForeignKey('producer.id'),
        primary_key=True
    )

    track = relationship(Track, backref=backref("track_producer"))
    producer = relationship(Producer, backref=backref("track_producer"))
