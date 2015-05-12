import os.path
import scipy.io.wavfile
import medleydb.multitrack
from sqlalchemy import Table, ForeignKey, Column, MetaData
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship, synonym, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


from . import utils

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

__all__ = [
    "Taxon",
    "Instrument",
    "Track",
    "Stem",
    "Raw",
    "Melody",
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


class Taxon(DeclarativeBase):
    """ One entry in the taxonomy. May have one or more taxa or instruments
    as children

    """
    __tablename__ = 'taxon'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), unique=True, nullable=False)
    """ Name of this taxonomy taxon """

    parent_id = Column(Integer, ForeignKey('taxon.id'))
    """ Parent taxon id """
    parent = relationship('Taxon', backref='children', remote_side=[id])
    """ Parent taxon. Inverse relation can be referenced using
    :code:`children`"""
    instruments = relationship('Instrument', backref='taxon', lazy="dynamic")
    """ Instruments belonging to this taxon """

    def __repr__(self):
        return '<Taxon: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Instrument(DeclarativeBase):
    """ An instrument. Always a child of a Taxon. Has stems and raws.

    """
    __tablename__ = 'instrument'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), unique=True, nullable=False)
    """ Name of the instrument """

    taxon_id = Column(Integer, ForeignKey('taxon.id'))
    """ Foreign key pointing to taxon,
    can be accessed using :code:`taxon` """
    stems = relationship('Stem', backref='instrument', lazy="dynamic")
    """ Stems associated to this instrument """
    raws = relationship('Raw', backref='instrument', lazy="dynamic")
    """ Raws associated to this instrument """

    def __repr__(self):
        return '<Instrument: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Track(DeclarativeBase):
    """ A track. Has stems, melodies, composers and producers.

    """
    __tablename__ = 'track'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), unique=True, nullable=False)
    """ Title of the track """
    artist = Column(Unicode(256), nullable=False)
    """ Artist """
    excerpt = Column(Boolean)
    """ Track is an excerpt """
    genre = Column(Unicode(256), nullable=False)
    """ Artist """
    has_bleed = Column(Boolean)
    """ Track has bleed """
    instrumental = Column(Boolean)
    """ Track is instrumental """
    data_dir = Column(Unicode(256), unique=True, nullable=False)
    """ Data directory of track, all files lie in this directory """
    metadata_filename = Column(Unicode(256), unique=True, nullable=False)
    """ Metadata filename of track """
    mix_filename = Column(Unicode(256), unique=True, nullable=False)
    origin = Column(Unicode(256), nullable=False)
    """ Origin of track (label, artist etc.) """
    raw_dir = Column(Unicode(256), nullable=False)
    """ Directory where all raw files are located in """
    stem_dir = Column(Unicode(256), nullable=False)
    """ Directory where all stem files are located in """
    website = Column(Unicode(256), nullable=False)
    """ Website associated with track """
    duration = Column(Integer, nullable=False)
    """ Number of seconds of audio file """

    stems = relationship('Stem', backref='track', lazy="dynamic")
    """ Stems associated with this track """
    melodies = relationship('Melody', backref='track', lazy="dynamic")
    """ Melodies associated with this track """
    composers = association_proxy(
        'track_composer', 'composer',
        creator=lambda composer: TrackComposer(composer=composer)
    )
    """ Composers associated with this track """
    producers = association_proxy(
        'track_producer', 'producer',
        creator=lambda producer: TrackProducer(producer=producer)
    )
    """ Producers associated with this track """

    @hybrid_property
    def base_dir(self):
        """ Get directory where all files are in """
        return os.path.join(
            os.environ['MEDLEYDB_PATH'],
            self.data_dir,
        )

    @hybrid_property
    def audio_path(self):
        """ Get path of mixed audio """
        return os.path.join(
            self.base_dir,
            self.mix_filename,
        )

    @hybrid_property
    def audio_data(self):
        """ Get mixed audio """
        return scipy.io.wavfile.read(self.audio_path)

    @hybrid_property
    def pitch_data(self):
        """ Get pitch annotation """
        fname = medleydb.multitrack._PITCH_FMT % \
            os.path.basename(self.metadata_filename).split('.')[0]
        pitch_annotation_fpath = os.path.join(
            medleydb.multitrack.PITCH_DIR,
            fname
        )
        return medleydb.multitrack.read_annotation_file(
            pitch_annotation_fpath,
            num_cols=2
        )

    @hybrid_property
    def metadata_path(self):
        """ Get path of metadata file """
        return os.path.join(
            self.base_dir,
            self.metadata_filename,
        )

    @hybrid_property
    def track_id(self):
        """ Get a special track_id string, format taken from MedleyDB """
        return medleydb.multitrack._TRACKID_FMT % (self.artist, self.name)

    @classmethod
    def from_medleydb(cls, instance, session):
        """ Create object instance from MedleyDB data """

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
                Stem.from_medleydb(stem, session, name=key, track=tmp)

            for dire, fmt in (
                (
                    medleydb.multitrack._MELODY1_DIR,
                    medleydb.multitrack._MELODY1_FMT
                ),
                (
                    medleydb.multitrack._MELODY2_DIR,
                    medleydb.multitrack._MELODY2_FMT
                ),
                (
                    medleydb.multitrack._MELODY3_DIR,
                    medleydb.multitrack._MELODY3_FMT
                )
            ):
                Melody.from_medleydb(
                    os.path.join(dire, fmt % tmp.track_id),
                    session, track=tmp
                )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Track: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Stem(DeclarativeBase):
    """ A stem. Belongs to a track and instrument and has raws.

    """
    __tablename__ = 'stem'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), nullable=False)
    """ Stem shortname """
    filename = Column(Unicode(256), unique=True, nullable=False)
    """ Audio filename """
    component = Column(Unicode(256))
    """ Type of component (vocal, bass etc.) """
    rank = Column(Integer, nullable=True)
    """ Rank of stem in track. Lower number => more important component
    to overall melody """

    track_id = Column(Integer, ForeignKey('track.id'))
    """ Track foreign key, can be accessed using :code:`track` """
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    """ Instrument foreign key, can be accessed using :code:`instrument` """
    raws = relationship('Raw', backref='stem', lazy="dynamic")
    """ Raw audio recordings associated to this stem """

    @hybrid_property
    def audio_path(self):
        """ Get audio filename """
        return os.path.join(
            self.track.base_dir,
            self.track.stem_dir,
            self.filename
        )

    @hybrid_property
    def audio_data(self):
        """ Read stem audio """
        return scipy.io.wavfile.read(self.audio_path)

    @hybrid_property
    def annotation_path(self):
        """ Get annotation filename """
        return os.path.splitext(
            self.filename
        )[0] + '.csv'

    @classmethod
    def from_medleydb(cls, instance, session, name='', track=None):
        """ Create object instance from MedleyDB data """
        tmp = cls(
            name=name,
            filename=instance['filename'],
            component=instance['component'],
            instrument=get_or_create(
                session, Instrument, name=instance['instrument']
            ),
            track=track
        )

        tmp.rank = utils.get_rankings(tmp)

        for key, raw in list(instance['raw'].items()):
            Raw.from_medleydb(raw, session, name=key, stem=tmp)

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Stem: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Raw(DeclarativeBase):
    """ A stem. Belongs to a stem and instrument.

    """
    __tablename__ = 'raw'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), nullable=False)
    """ Raw shorthandle """
    filename = Column(Unicode(256), unique=True, nullable=False)
    """ Audio filename """

    stem_id = Column(Integer, ForeignKey('stem.id'))
    """ Stem foreign key, can be accessed using :code:`stem` """
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    """ Instrument foreign key, can be accessed using :code:`instrument` """

    @hybrid_property
    def audio_path(self):
        """ Get filename of audio """
        return os.path.join(
            self.stem.track.base_dir,
            self.stem.track.raw_dir,
            self.filename
        )

    @hybrid_property
    def audio_data(self):
        """ Read raw audio """
        return scipy.io.wavfile.read(self.audio_path)

    @classmethod
    def from_medleydb(cls, instance, session, name='', stem=None):
        """ Create object instance from MedleyDB data """
        tmp = cls(
            name=name,
            filename=instance['filename'],
            instrument=get_or_create(
                session, Instrument, name=instance['instrument']
            ),
            stem=stem
        )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Raw: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Melody(DeclarativeBase):
    """ A melody. Belongs to a track.

    """
    __tablename__ = 'melody'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    filename = Column(Unicode(256), unique=True, nullable=False)
    """ Annotation filename """

    track_id = Column(Integer, ForeignKey('track.id'))
    """ Track foreign key, can be accessed using :code:`track` """

    @hybrid_property
    def annotation_path(self):
        """ Get filename of annotation """
        return os.path.join(
            medleydb.multitrack.MELODY_DIR,
            self.filename
        )

    @hybrid_property
    def annotation_data(self):
        """ Read melody annotation """
        return medleydb.multitrack.read_annotation_file(self.annotation_path)

    @classmethod
    def from_medleydb(cls, filename, session, track=None):
        """ Create object instance from MedleyDB data """
        tmp = cls(
            filename=filename,
            track=track
        )

        session.add(tmp)
        session.commit()
        return tmp

    def __repr__(self):
        return '<Melody: filename=%s>' % unicode(self)

    def __unicode__(self):
        return self.filename


class Composer(DeclarativeBase):
    """ A copmoser. Belongs to one or more tracks.

    """
    __tablename__ = 'composer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), unique=True, nullable=False)
    """ Composer name """

    tracks = association_proxy(
        'track_composer', 'track',
        creator=lambda track: TrackComposer(track=track)
    )
    """ Tracks associated with this composer """

    def __repr__(self):
        return '<Composer: name=%s>' % unicode(self)

    def __unicode__(self):
        return self.name


class Producer(DeclarativeBase):
    """ A producer. Belongs to one or more tracks.

    """
    __tablename__ = 'producer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    """ Unique entry id. Every entry in every table has one. """
    name = Column(Unicode(256), unique=True, nullable=False)
    """ Producer name """

    tracks = association_proxy(
        'track_producer', 'track',
        creator=lambda track: TrackProducer(track=track)
    )
    """ Tracks associated with this producer """

    def __repr__(self):
        return '<Producer: name=%s>' % unicode(self)

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
