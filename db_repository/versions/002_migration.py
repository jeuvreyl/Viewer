from sqlalchemy import *


pre_meta = MetaData()
post_meta = MetaData()
uploaded_image = Table('uploaded_image', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fileName', String(length=128)),
    Column('file', LargeBinary),
    Column('owner_id', Integer),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_image'].columns['owner_id'].create()
    pre_meta.tables['user'].columns['email'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['uploaded_image'].columns['owner_id'].drop()
    pre_meta.tables['user'].columns['email'].create()
