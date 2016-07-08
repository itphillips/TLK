from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
word_sentence_positions = Table('word_sentence_positions', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('ws_linear_position', INTEGER),
    Column('id_sentence', INTEGER),
    Column('id_word', INTEGER),
)

words = Table('words', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word', String(length=60)),
    Column('pos', String(length=40)),
    Column('ws_linear_position', Integer),
    Column('id_sentence', Integer),
    Column('id_user', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['word_sentence_positions'].drop()
    post_meta.tables['words'].columns['ws_linear_position'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['word_sentence_positions'].create()
    post_meta.tables['words'].columns['ws_linear_position'].drop()
