__author__ = 'lolo'

from Viewer import db
from werkzeug.security import generate_password_hash, check_password_hash


class UploadedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128), index=True, unique=True)
    file = db.Column(db.LargeBinary())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thumbnail = db.relationship("UploadedThumbnail", backref="uploaded_image", uselist=False, cascade="all, delete, delete-orphan")

    def __init__(self, file_name, file):
        self.file_name = file_name
        self.file = file


class UploadedThumbnail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128), index=True, unique=True)
    file = db.Column(db.LargeBinary())
    uploadedImage_id = db.Column(db.Integer,  db.ForeignKey('uploaded_image.id'))

    def __init__(self, file_name, file):
        self.file_name = file_name
        self.file = file


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128), index=True)
    images = db.relationship("UploadedImage", backref="user", lazy="dynamic")

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return "<User {}>".format(self.username)