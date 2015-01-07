from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
uploaded_thumbnail = Table('uploaded_thumbnail', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('file_name', String(length=128)),
    Column('file', LargeBinary),
    Column('uploadedImage', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_thumbnail'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_thumbnail'].drop()
