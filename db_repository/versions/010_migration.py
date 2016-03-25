from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
phrase_sentence_positions = Table('phrase_sentence_positions', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ps_linear_position', Integer),
    Column('id_phrase', Integer),
    Column('id_sentence', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrase_sentence_positions'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrase_sentence_positions'].drop()
