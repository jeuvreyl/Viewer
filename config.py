__author__ = 'lolo'

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfiguration:
    SIZE = 200, 200
    COMMIT_STEP = 50
    PLACEHOLDER_FOLDER = os.path.join(basedir, 'static/media')
    PLACEHOLDER_THUMBNAIL_NAME = 'placeholder.gif'


class ProdConfiguration(BaseConfiguration):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'Viewer.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'
    IMAGES_PER_PAGE = 48


class TestConfiguration(BaseConfiguration):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    IMAGES_PER_PAGE = 12
    TEST_RESOURCES_PATH = os.path.join(basedir, 'test_resources')