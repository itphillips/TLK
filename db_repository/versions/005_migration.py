from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
phrases = Table('phrases', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('phrase', String(length=60)),
    Column('phrase_type', String(length=30)),
    Column('phrase_subtype', String(length=30)),
    Column('sentenceid', Integer),
)

words = Table('words', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('word', VARCHAR(length=30)),
    Column('gram_case', VARCHAR(length=30)),
    Column('sentence_id', INTEGER),
    Column('language', VARCHAR(length=30)),
    Column('pos', VARCHAR(length=30)),
)

words = Table('words', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word', String(length=30)),
    Column('pos', String(length=30)),
    Column('gram_case', String(length=30)),
    Column('sentenceid', Integer),
    Column('language', String(length=30)),
)

words_phrases = Table('words_phrases', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('wordid', Integer),
    Column('phraseid', Integer),
    Column('position', Integer),
    Column('sentenceid', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrases'].columns['sentenceid'].create()
    pre_meta.tables['words'].columns['sentence_id'].drop()
    post_meta.tables['words'].columns['sentenceid'].create()
    post_meta.tables['words_phrases'].columns['sentenceid'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrases'].columns['sentenceid'].drop()
    pre_meta.tables['words'].columns['sentence_id'].create()
    post_meta.tables['words'].columns['sentenceid'].drop()
    post_meta.tables['words_phrases'].columns['sentenceid'].drop()
