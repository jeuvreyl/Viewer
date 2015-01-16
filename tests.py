__author__ = 'lolo'

import os
from io import BytesIO

from flask import url_for
from flask_testing import TestCase
from Viewer import app, db
from Viewer.models import UploadedImage, User, UploadedThumbnail


TEST_FILENAME = "image.jpeg"
TEST_FILE_CONTENT = b"my file contents"


def prepare_test_image_in_db():
    """
    Prepare a dummy image with a thumbnail and insert them in database
    """
    test_image = UploadedImage(file_name=TEST_FILENAME, file=TEST_FILE_CONTENT)
    test_thumbnail = UploadedThumbnail(file_name=TEST_FILENAME, file=TEST_FILE_CONTENT)
    test_image.thumbnail = test_thumbnail
    db.session.add(test_image)
    db.session.commit()
    images_names = list()
    images_names.append(TEST_FILENAME)
    return images_names


def prepare_test_images_in_db():
    """
    Prepare a dummy image with a thumbnail and insert them in database
    """
    test_filename = "image.jpeg"
    file_content = b"my file contents"
    images_names = list()
    for i in range(10):
        image_name = test_filename + str(i)
        test_image = UploadedImage(file_name=image_name, file=file_content)
        test_thumbnail = UploadedThumbnail(file_name=test_filename + str(i), file=file_content)
        test_image.thumbnail = test_thumbnail
        db.session.add(test_image)
        images_names.append(image_name)
    db.session.commit()
    return images_names


class BaseTestCase(TestCase):
    """A base test case """

    def create_app(self):
        app.config.from_object('Viewer.config.TestConfiguration')
        test_user = User('test', 'test')
        db.session.add(test_user)
        return app

    def setUp(self):
        db.create_all()
        self.login('test', 'test')

    def setDown(self):
        self.logout()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            user_name=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


class ListTestCase(BaseTestCase):
    """ List screen test """

    def test_list_screen(self):
        """
        Test access to list screen
        """
        response = self.client.get(url_for("list_images"))
        assert response.get_data(), "Nothing has been returned"
        assert response.mimetype == "text/html", "Wrong mimeType returned"
        self.assert200(response, "Wrong response code")
        assert b"add images" in response.data, "Wrong page"

    def test_paginate_list_screen(self):
        """
        Test pagination of list screen
        Images per page is set to 6 and the result of a GET request
        is checked to have six images
        """
        self.app.config['IMAGES_PER_PAGE'] = 6
        prepare_test_images_in_db()
        response = self.client.get(url_for("list_images"))
        assert response.get_data(), "Nothing has been returned"
        assert response.mimetype == "text/html", "Wrong mimeType returned"
        self.assert200(response, "Wrong response code")
        number_of_images_displayed = response.data.count(b"image_number_")
        assert number_of_images_displayed == 6, "Wrong number of images displayed, actual : {}".format(
            number_of_images_displayed)


class ImageTestCase(BaseTestCase):
    def verify_delete_in_db(self, image_names_list, number_expected):
        number_of_images = UploadedImage.query.filter(UploadedImage.file_name.in_(image_names_list)).count()
        assert number_of_images == number_expected, '{} files have been retrieved from database'.format(
            number_of_images)
        number_of_thumbnails = UploadedThumbnail.query.filter(UploadedThumbnail.file_name.in_(image_names_list)).count()
        assert number_of_thumbnails == number_expected, '{} files have been retrieved from database'.format(
            number_of_thumbnails)

    def assert_file_in_db(self, saved_file, test_file_content, test_filename):
        assert saved_file.file_name == test_filename, 'Wrong filename : {}'.format(saved_file.file_name)
        assert saved_file.file, 'No content has been saved'
        assert saved_file.file == test_file_content, 'No content has been saved'

    def test_upload(self):
        """
        upload a file using the upload route and verify its presence in DB with the appropriate thumbnail generated
        """

        test_filename = "test.jpg"
        test_thumbnail_filename = "test_thumbnail.jpg"
        with open(os.path.join(self.app.config['TEST_RESOURCES_PATH'], test_filename), "rb") as f:
            test_file_content = f.read()
        with open(os.path.join(self.app.config['TEST_RESOURCES_PATH'], test_thumbnail_filename), "rb") as f:
            test_file_thumbnail_content = f.read()

        response = self.client.post(url_for("upload"),
                                    data=dict(uploaded_images=(BytesIO(test_file_content), test_filename)))
        self.assert_redirects(response, url_for('list_images'))

        db_result = UploadedImage.query.filter(UploadedImage.file_name == test_filename).all()
        number_of_images = len(db_result)
        assert number_of_images == 1, '{} files have been retrieved from database'.format(number_of_images)
        saved_file = db_result[0]

        self.assert_file_in_db(saved_file, test_file_content, test_filename)

        saved_thumbnail = saved_file.thumbnail
        self.assert_file_in_db(saved_thumbnail, test_file_thumbnail_content, test_filename)

    def test_upload_duplicates(self):
        """
        Insert an image in database, and upload another one with the same filename
        Must display 'image image.jpeg is already in DB' message
        """
        prepare_test_image_in_db()
        response = self.client.post(url_for("upload"),
                                    data=dict(uploaded_images=(BytesIO(TEST_FILE_CONTENT), TEST_FILENAME)),
                                    follow_redirects=True)
        assert b"image image.jpeg is already in DB" in response.data, "Duplicate image has not been detected"

    def test_get_image(self):
        """
        Insert an image in DB and retrieve it by a get request on /image/ route
        """
        prepare_test_image_in_db()
        response = self.client.get(url_for("image", image_id=1))
        assert response.get_data(), "Nothing has been returned"
        assert response.mimetype == "image/jpeg", "Wrong mimeType returned"
        self.assert200(response, "Wrong response code")
        assert TEST_FILE_CONTENT in response.data, "wrong content retrieved"

    def test_delete_one_image(self):
        """
        Insert an image, delete it by request on /delete/ route and check again in DB
        """
        image_name = prepare_test_image_in_db()
        with self.client:
            response = self.client.post(url_for("delete_images"),
                                        data=dict(ids=["1"]))
        self.assert_redirects(response, url_for('list_images'))
        self.verify_delete_in_db(image_name, number_expected=0)

    def test_delete_several_images(self):
        """
        Insert 10 images, delete them by request on /delete/ route and check again in DB
        """
        image_names = prepare_test_images_in_db()
        response = self.client.post(url_for("delete_images"),
                                    data=dict(ids=[str(i) for i in range(1, 11)]))
        self.assert_redirects(response, url_for('list_images'))
        self.verify_delete_in_db(image_names, number_expected=0)

    def test_delete_no_image(self):
        """
        Insert an image, post no ids by request on /delete/ route and check again in DB
        """
        image_name = prepare_test_image_in_db()
        response = self.client.post(url_for("delete_images"),
                                    data=dict(ids=[]))
        self.assert_redirects(response, url_for('list_images'))
        self.verify_delete_in_db(image_name, number_expected=1)