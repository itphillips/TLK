from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
sentences = Table('sentences', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('sessionid', String(length=10)),
    Column('sessionnumber', Integer),
    Column('sentence', String(length=140)),
    Column('sentence_type', String(length=30)),
    Column('language', String(length=50)),
    Column('english_gloss', String(length=140)),
    Column('collection_date', String(length=70)),
    Column('collection_location', String(length=70)),
    Column('notes', String(length=140)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['sentences'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['sentences'].columns['user_id'].drop()
