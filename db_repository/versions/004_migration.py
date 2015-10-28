from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
sentences = Table('sentences', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('sessionID', VARCHAR(length=3)),
    Column('session_number', INTEGER),
    Column('sentence', VARCHAR(length=90)),
    Column('sentence_type', VARCHAR(length=30)),
    Column('language', VARCHAR(length=25)),
    Column('english_gloss', VARCHAR(length=140)),
    Column('collection_date', VARCHAR(length=70)),
    Column('collection_location', VARCHAR(length=70)),
    Column('notes', VARCHAR(length=140)),
    Column('timestamp', TIMESTAMP),
    Column('user_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['sentences'].columns['collection_date'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['sentences'].columns['collection_date'].create()
