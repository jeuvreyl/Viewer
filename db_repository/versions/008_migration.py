from sqlalchemy import *


pre_meta = MetaData()
post_meta = MetaData()
uploaded_thumbnail = Table('uploaded_thumbnail', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('file_name', VARCHAR(length=128)),
    Column('file', BLOB),
    Column('uploadedImage', INTEGER),
)

uploaded_image = Table('uploaded_image', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('file_name', String(length=128)),
    Column('file', LargeBinary),
    Column('user_id', Integer),
    Column('thumbnail', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['uploaded_thumbnail'].columns['uploadedImage'].drop()
    post_meta.tables['uploaded_image'].columns['thumbnail'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['uploaded_thumbnail'].columns['uploadedImage'].create()
    post_meta.tables['uploaded_image'].columns['thumbnail'].drop()
