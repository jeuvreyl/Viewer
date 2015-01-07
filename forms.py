
__author__ = 'lolo'

from flask_wtf.form import Form
from wtforms.fields import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from Viewer import db
from Viewer.models import User


class UploadImageForm(Form):
    to_delete = BooleanField(label='Image to be deleted', default=False)


class LoginForm(Form):
    user_name = StringField(label="User name", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])

    def validate_login(self, _):
        user = self.get_user()
        if user is None:
            raise ValidationError('Invalid user')
        # we're comparing the plaintext pw with the the hash from the db
        if not user.check_password(self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter(User.username == self.user_name.data).first()


class RegistrationForm(Form):
    user_name = StringField(label="User name", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])

    def validate_login(self, _):
        if db.session.query(User).filter(User.username == self.user_name.data).count() > 0:
            raise ValidationError('Duplicate username')