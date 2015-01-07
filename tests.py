import os

__author__ = 'lolo'

from flask import url_for
from flask_testing import TestCase
from Viewer import app, db
from io import BytesIO
from Viewer.models import UploadedImage, User, UploadedThumbnail


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
        :return:
        """
        response = self.client.get(url_for("list_images"))
        self.assertIsNot(response.get_data(), "Nothing has been returned")
        self.assertTrue(response.mimetype == "text/html", "Wrong mimeType returned")
        self.assert200(response, "Wrong response code")
        self.assertTrue(b"add images" in response.data, "Wrong page")

    def test_paginate_list_screen(self):
        """
        Test pagination of list screen
        Images per page is setted to 6 and the result of a GET request
        is checked to have six images
        :return:
        """
        test_filename = "image.jpeg"
        file_content = b"my file contents"
        self.app.config['IMAGES_PER_PAGE'] = 6
        for i in range(10):
            test_image = UploadedImage(file_name=test_filename + str(i), file=file_content)
            test_thumbnail = UploadedThumbnail(file_name=test_filename + str(i), file=file_content)
            test_image.thumbnail = test_thumbnail
            db.session.add(test_image)
        db.session.commit()
        response = self.client.get(url_for("list_images"))
        self.assertIsNot(response.get_data(), "Nothing has been returned")
        self.assertTrue(response.mimetype == "text/html", "Wrong mimeType returned")
        self.assert200(response, "Wrong response code")
        number_of_images_displayed = response.data.count(b"image_number_")
        self.assertTrue( number_of_images_displayed == 6, "Wrong number of images displayed, actual : {}".format(number_of_images_displayed))

    def test_upload(self):
        """
        upload a file using the upload/ route and verify its presence in DB
        :return:
        """

        test_filename = "test.jpg"
        test_thumbnail_filename = "test_thumbnail.jpg"
        with open(os.path.join(self.app.config['TEST_RESOURCES_PATH'], test_filename), "rb") as f:
            test_file_content = f.read()
        with open(os.path.join(self.app.config['TEST_RESOURCES_PATH'], test_thumbnail_filename), "rb") as f:
            test_file_thumbnail_content = f.read()

        with self.client:
            response = self.client.post(url_for("upload"),
                                        data=dict(uploaded_images=(BytesIO(test_file_content), test_filename)))
        self.assert_redirects(response, url_for('list_images'))

        db_result = UploadedImage.query.filter(UploadedImage.file_name == test_filename).all()
        self.assertTrue(len(db_result) == 1, '{} files have been retrieved from database'.format(len(db_result)))
        saved_file = db_result[0]

        self.assertTrue(saved_file.file_name == test_filename, 'Wrong filename : {}'.format(saved_file.file_name))
        self.assertTrue(saved_file.file, 'No content has been saved')
        self.assertTrue(saved_file.file == test_file_content, 'No content has been saved')

        saved_thumbnail = saved_file.thumbnail
        self.assertTrue(saved_thumbnail.file_name == test_filename, 'Wrong filename : {}'.format(saved_file.file_name))
        self.assertTrue(saved_thumbnail.file, 'No content has been saved')
        self.assertTrue(saved_thumbnail.file == test_file_thumbnail_content, 'No content has been saved')

    def test_get_image(self):
        """
        Insert an image in DB and retrieve it by a get request on /image/ route
        :return:
        """
        test_filename = "image.jpeg"
        file_content = b"my file contents"
        test_image = UploadedImage(file_name=test_filename, file=file_content)
        db.session.add(test_image)
        db.session.commit()
        with self.client:
            response = self.client.get(url_for("image", image_id=1))
        self.assertIsNot(response.get_data(), "Nothing has been returned")
        self.assertTrue(response.mimetype == "image/jpeg", "Wrong mimeType returned")
        self.assert200(response, "Wrong response code")
        self.assertTrue(file_content in response.data, "wrong content retrieved")

    def test_delete_image(self):
        """
        Insert an image, delete it by request on /delete/ route and check again in DB
        :return:
        """
        test_filename = "image.jpeg"
        file_content = b"my file contents"
        test_image = UploadedImage(file_name=test_filename, file=file_content)
        test_thumbnail = UploadedThumbnail(file_name=test_filename, file=file_content)
        test_image.thumbnail = test_thumbnail
        test_image.to_delete = True
        db.session.add(test_image)
        db.session.commit()
        with self.client:
            response = self.client.post(url_for("delete_images"),
                                        data=dict(ids=["1"]))
        self.assert_redirects(response, url_for('list_images'))
        image_db_result = UploadedImage.query.filter(UploadedImage.file_name == test_filename).all()
        self.assertTrue(len(image_db_result) == 0,
                        '{} files have been retrieved from database'.format(len(image_db_result)))

        thumbnail_db_result = UploadedThumbnail.query.filter(UploadedThumbnail.file_name == test_filename).all()
        self.assertTrue(len(thumbnail_db_result) == 0,
                        '{} files have been retrieved from database'.format(len(thumbnail_db_result)))