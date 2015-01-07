from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=128)),
    Column('password', String(length=128)),
)

uploaded_image = Table('uploaded_image', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('file_name', String(length=128)),
    Column('file', LargeBinary),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].create()
    post_meta.tables['uploaded_image'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].drop()
    post_meta.tables['uploaded_image'].columns['user_id'].drop()
