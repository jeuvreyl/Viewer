from flask_login import UserMixin

__author__ = 'lolo'

from Viewer import db
from werkzeug.security import generate_password_hash, check_password_hash


class UploadedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128), unique=True)
    file = db.Column(db.LargeBinary())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thumbnail = db.relationship("UploadedThumbnail", backref="uploaded_image", uselist=False, cascade="all, delete, delete-orphan")

    def __init__(self, file_name, file, user):
        self.file_name = file_name
        self.file = file
        self.user = user

    def __repr__(self):
        return "<image {}>".format(self.file_name)


class UploadedThumbnail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128))
    file = db.Column(db.LargeBinary())
    uploadedImage_id = db.Column(db.Integer,  db.ForeignKey('uploaded_image.id'))

    def __init__(self, file_name, file):
        self.file_name = file_name
        self.file = file

    def __repr__(self):
        return "<thumbnail {}>".format(self.file_name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    images = db.relationship("UploadedImage", backref="user", lazy="dynamic")

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.username)