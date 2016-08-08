from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
sentences = Table('sentences', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('sessionid', VARCHAR(length=40)),
    Column('sessionnumber', INTEGER),
    Column('sentence', VARCHAR),
    Column('sentence_type', VARCHAR(length=30)),
    Column('sentence_language', VARCHAR(length=50)),
    Column('english_gloss', VARCHAR),
    Column('collection_date', TIMESTAMP),
    Column('collection_location', VARCHAR(length=70)),
    Column('notes', VARCHAR(length=140)),
    Column('timestamp', TIMESTAMP),
    Column('id_user', INTEGER),
)

sentences = Table('sentences', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('sessionid', String(length=40)),
    Column('sessionnumber', Integer),
    Column('sentence', String),
    Column('sentence_type', String(length=30)),
    Column('sentence_language', String(length=50)),
    Column('english_gloss', String),
    Column('collection_date', DateTime),
    Column('collection_location', String(length=70)),
    Column('notes', String),
    Column('inputdate', DateTime),
    Column('id_user', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['sentences'].columns['timestamp'].drop()
    post_meta.tables['sentences'].columns['inputdate'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['sentences'].columns['timestamp'].create()
    post_meta.tables['sentences'].columns['inputdate'].drop()
