
__author__ = 'lolo'

from io import BytesIO
from flask import render_template, flash, redirect, url_for, send_file, request, g
from Viewer import app, db, login_manager
from Viewer.forms import UploadImageForm, RegistrationForm, LoginForm
from Viewer.models import UploadedImage, User, UploadedThumbnail
from werkzeug.utils import secure_filename
from sqlalchemy.orm import exc
from werkzeug.exceptions import abort
from flask_login import login_user, login_required, logout_user, current_user
from wtforms.validators import ValidationError
from PIL import Image, ImageOps


@app.route('/list', methods=['GET'])
@app.route('/list/<int:page>', methods=['GET'])
@login_required
def list_images(page=1):
    form = UploadImageForm()
    images_ids = UploadedImage.query.with_entities(UploadedImage.id, UploadedThumbnail.id).join(
        UploadedThumbnail).paginate(page, app.config[
        "IMAGES_PER_PAGE"], False)
    return render_template('list.html',
                           title='Images listing',
                           images_ids=images_ids,
                           form=form)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    form = UploadImageForm()
    if form.validate_on_submit():
        for number, file in enumerate(request.files.getlist('uploaded_images')):
            if file:
                image_name = secure_filename(file.filename)
                fake_file = BytesIO()
                file.save(fake_file)
                fake_file.seek(0)
                image_thumbnail = generate_thumbnail(image_name, fake_file)
                fake_file.seek(0)
                image_to_save = UploadedImage(image_name, fake_file.read())
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
    ids = request.form.getlist('ids')
    images_to_delete = UploadedImage.query.filter(UploadedImage.id.in_(ids)).all()
    for number, image_to_delete in enumerate(images_to_delete):
        db.session.delete(image_to_delete)
        if number % app.config["IMAGES_PER_PAGE"] == 0:
                    db.session.commit()
    db.session.commit()
    return redirect(url_for('list_images'))


@app.route('/image/<int:image_id>', methods=['GET'])
@login_required
def image(image_id):
    uploaded_image = _get_image_or_404(image_id)
    return send_file(BytesIO(uploaded_image.file), attachment_filename=uploaded_image.file_name)


def _get_image_or_404(image_id):
    try:
        return UploadedImage.query.filter_by(id=image_id).one()
    except exc.NoResultFound or exc.MultipleResultsFound:
        abort(404)


@app.route('/thumbnail/<int:thumbnail_id>', methods=['GET'])
@login_required
def thumbnail(thumbnail_id):
    uploaded_thumbnail = _get_thumbnail_or_404(thumbnail_id)
    return send_file(BytesIO(uploaded_thumbnail.file), attachment_filename=uploaded_thumbnail.file_name)


def _get_thumbnail_or_404(image_id):
    try:
        return UploadedThumbnail.query.filter_by(id=image_id).one()
    except exc.NoResultFound or exc.MultipleResultsFound:
        abort(404)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    return user


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            form.validate_login(None)
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
    logout_user()
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = current_user


def generate_thumbnail(filename, content):
    extension = filename.split(".")[-1]

    if extension == "jpg":
        extension = "jpeg"

    if extension.upper() not in ['GIF', 'JPEG', 'PNG', 'BMP']:
        return None

    image_to_work_on = Image.open(content)
    thumb = ImageOps.fit(image_to_work_on, (app.config["SIZE"]), Image.ANTIALIAS)

    fake_file = BytesIO()
    thumb.save(fake_file, format=extension)
    fake_file.seek(0)

    return UploadedThumbnail(filename, fake_file.read())