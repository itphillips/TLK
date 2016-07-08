from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
words = Table('words', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('word', VARCHAR(length=30)),
    Column('partofspeech', VARCHAR(length=30)),
    Column('gram_case', VARCHAR(length=30)),
    Column('sentence_id', INTEGER),
    Column('language', VARCHAR(length=30)),
)

words = Table('words', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word', String(length=30)),
    Column('pos', String(length=30)),
    Column('gram_case', String(length=30)),
    Column('sentence_id', Integer),
    Column('language', String(length=30)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['words'].columns['partofspeech'].drop()
    post_meta.tables['words'].columns['pos'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['words'].columns['partofspeech'].create()
    post_meta.tables['words'].columns['pos'].drop()
