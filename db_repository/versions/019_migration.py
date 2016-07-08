from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
phrase_structure_rules = Table('phrase_structure_rules', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('phrase_structure', String(length=60)),
    Column('id_phrase', Integer),
    Column('id_user', Integer),
    Column('id_sentence', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrase_structure_rules'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['phrase_structure_rules'].drop()
