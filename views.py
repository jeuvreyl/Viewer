__author__ = 'lolo'

from io import BytesIO
from flask import render_template, flash, redirect, url_for, send_file, request, g
from Viewer import app, login_manager, db
from Viewer.models import UploadedImage, User, UploadedThumbnail
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from PIL import Image, ImageOps
from flask_wtf.form import Form
from wtforms.fields import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError
import os

class UploadImageForm(Form):
    """
    Form used for image deletion on the image list view
    """
    to_delete = BooleanField(label='Image to be deleted', default=False)


class LoginForm(Form):
    """
    Login form
    """
    user_name = StringField(label="User name", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])

    def validate_login(self, _):
        """
        """
        user = db.session.query(User).filter(User.username == self.user_name.data).first()
        if user is None:
            raise ValidationError('Invalid user')
        if not user.check_password(self.password.data):
            raise ValidationError('Invalid password')


class RegistrationForm(Form):
    """
    Registration form
    """
    user_name = StringField(label="User name", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])

    def check_duplicates(self, _):
        """
        """
        if db.session.query(User).filter(User.username == self.user_name.data).count() > 0:
            raise ValidationError('Duplicate username')


@app.route('/list', methods=['GET'])
@app.route('/list/<int:page>', methods=['GET'])
@login_required
def list_images(page=1):
    """
    Image list view
    Main view of the application
    :param page:
    :return:
    """
    form = UploadImageForm()
    images_ids = UploadedImage.query.with_entities(UploadedImage.id, UploadedThumbnail.id).filter(
        UploadedImage.user_id == current_user.id).join(
        UploadedThumbnail).paginate(page, app.config["IMAGES_PER_PAGE"], False)
    return render_template('list.html',
                           title='Images listing',
                           images_ids=images_ids,
                           form=form)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    """
    Route used for file upload
    A thumbnail is generated from the uploaded image
    :return:
    """
    form = UploadImageForm()
    if form.validate_on_submit():
        for number, file in enumerate(request.files.getlist('uploaded_images')):
            if file:
                image_name = secure_filename(file.filename)
                image_in_db = UploadedImage.query.filter(UploadedImage.file_name == image_name).first()
                if image_in_db:
                    flash("image {} is already in DB".format(image_name))
                else:
                    fake_file = BytesIO()
                    file.save(fake_file)
                    fake_file.seek(0)
                    image_thumbnail = _generate_thumbnail(image_name, fake_file)
                    fake_file.seek(0)
                    image_to_save = UploadedImage(image_name, fake_file.read(), current_user)
                    image_to_save.thumbnail = image_thumbnail
                    db.session.add(image_to_save)
                    flash('Image {} uploaded'.format(image_name), 'info')
                    if number % app.config["IMAGES_PER_PAGE"] == 0:
                        db.session.commit()
                db.session.commit()
    return redirect(url_for('list_images'))


@app.route('/delete', methods=['POST'])
@login_required
def delete_images():
    """
    Delete image route
    :return:
    """
    delete_ids = request.form.getlist('delete_ids')
    if delete_ids:
        images_to_delete = UploadedImage.query.filter(UploadedImage.id.in_(delete_ids)).filter(
            UploadedImage.user_id == current_user.id).all()
        for number, image_to_delete in enumerate(images_to_delete):
            db.session.delete(image_to_delete)
            if number % app.config["IMAGES_PER_PAGE"] == 0:
                db.session.commit()
        db.session.commit()
    return redirect(url_for('list_images'))


@app.route('/image/<int:image_id>', methods=['GET'])
@login_required
def image(image_id):
    """
    Get image route
    Used on the image list view to serve images files
    :param image_id:
    :return:
    """
    uploaded_image = UploadedImage.query.filter_by(id=image_id).first_or_404()
    return send_file(BytesIO(uploaded_image.file), attachment_filename=uploaded_image.file_name)


@app.route('/thumbnail/<int:thumbnail_id>', methods=['GET'])
@login_required
def thumbnail(thumbnail_id):
    """
    Get thumbnail route
    Used on the image list view to serve thumbnails files
    :param thumbnail_id:
    :return:
    """
    uploaded_thumbnail = UploadedThumbnail.query.filter_by(id=thumbnail_id).first_or_404()
    return send_file(BytesIO(uploaded_thumbnail.file), attachment_filename=uploaded_thumbnail.file_name)


@login_manager.user_loader
def load_user(user_id):
    """
    Helper function called by Flask-Login
    :param user_id:
    :return:
    """
    user = User.query.filter(User.id == user_id).first()
    return user


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registration route used with  the RegistrationForm
    :return:
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            form.check_duplicates(None)
        except ValidationError as err:
            flash("Registration failed : {}".format(err), "info")
            return redirect(url_for('register'))
        else:
            user = User(form.user_name.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered', "info")
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Registration route used with  the LoginForm
    :return:
    """
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('list_images'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            form.validate_login(None)
        except ValidationError as err:
            flash("Login failed : {}".format(err))
            return redirect(url_for('login'))
        else:
            user = User.query.filter(User.username == form.user_name.data).first()
            login_user(user)
            flash('User successfully logged in', "info")
            return redirect(url_for('list_images'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """
    Logout route
    :return:
    """
    logout_user()
    return redirect(url_for('login'))


@app.before_request
def before_request():
    """
    helper function trigger before managing a request
    used to find if an user is already logged or not (=> current_user is None)
    :return:
    """
    g.user = current_user


def _generate_thumbnail(filename, content):
    """
    Generate thumbnail from the given image using Pillow
    :param filename:
    :param content:
    :return:
    """
    extension = filename.split(".")[-1]

    if extension == "jpg":
        extension = "jpeg"

    if extension.upper() not in ['GIF', 'JPEG', 'PNG', 'BMP']:
        return _get_placeholder()

    try:
        image_to_work_on = Image.open(content)
        thumb = ImageOps.fit(image_to_work_on, (app.config["SIZE"]), Image.ANTIALIAS)
    except Exception as err:
        flash("Error {} as occured while converting image {} to thumbnail".format(err, filename))
        return _get_placeholder()
    else:
        fake_file = BytesIO()
        thumb.save(fake_file, format=extension)
        fake_file.seek(0)

    return UploadedThumbnail(filename, fake_file.read())


def _get_placeholder():
    placeholder_name = app.config["PLACEHOLDER_THUMBNAIL_NAME"]
    placeholder_full_path = os.path.join(app.config["PLACEHOLDER_FOLDER"], placeholder_name)
    with open(placeholder_full_path, "rb") as f:
        file_content = f.read()
    return UploadedThumbnail(placeholder_name, file_content)