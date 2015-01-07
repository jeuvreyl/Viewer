from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
uploaded_thumbnail = Table('uploaded_thumbnail', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('file_name', String(length=128)),
    Column('file', LargeBinary),
    Column('uploadedImage_id', Integer),
)

uploaded_image = Table('uploaded_image', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('file', BLOB),
    Column('file_name', VARCHAR(length=128)),
    Column('user_id', INTEGER),
    Column('thumbnail_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_thumbnail'].columns['uploadedImage_id'].create()
    pre_meta.tables['uploaded_image'].columns['thumbnail_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_thumbnail'].columns['uploadedImage_id'].drop()
    pre_meta.tables['uploaded_image'].columns['thumbnail_id'].create()
