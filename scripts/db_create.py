__author__ = 'lolo'


#!flask/bin/python
from migrate.versioning import api
from Viewer.config import ProdConfiguration
from Viewer import db
import os.path

SQLALCHEMY_DATABASE_URI = ProdConfiguration.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_MIGRATE_REPO = ProdConfiguration.SQLALCHEMY_MIGRATE_REPO

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))