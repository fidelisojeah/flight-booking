import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from app.accounts.tests import factory as user_factory


class AccountsProfilePicture(APITestCase):
    def setUp(self):
        self.cloudinary_patcher = patch('cloudinary.utils.cloudinary_url')
        self.cloudinary_upload_patcher = patch(
            'cloudinary.uploader.upload',
            side_effect=user_factory.CloudinaryMock.upload
        )
        self.mock_cloudinary = self.cloudinary_patcher.start()
        self.mock_cloudinary_upload = self.cloudinary_upload_patcher.start()

        self.user = user_factory.create_user(
            email='test@example.com',
            password='testuserpassword',
            username='testuser',
            first_name='example',
            last_name='demo'
        )
        self.valid_image = self._generate_fake_image(
            'valid_image.png',
            50,
            (225, 120, 220)
        )

    def _generate_fake_image(self, file_name, render_size=50, background_color=(200, 200, 200)):
        file = BytesIO()
        image = Image.new(
            'RGB',
            size=(render_size, render_size),
            color=background_color).save(file, 'PNG')

        file.name = file_name
        file.seek(0)
        return file

    def tearDown(self):
        self.cloudinary_patcher.stop()
        self.cloudinary_upload_patcher.stop()
        self.user.delete()


class AccountsProfilePictureExceptions(AccountsProfilePicture):
    '''Handle Profile Picture Upload/Retrieve/Delete - When not valid'''

    def test_update_image_no_image(self):
        '''Updating Profile Picture - Invalid :-When no Image is sent for upload'''

        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            format='multipart')

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['message'],
            'No file was submitted.'
        )
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['type'],
            'required'
        )

    def test_update_image_invalid_image(self):
        '''Updating Profile Picture - Invalid :- When Image is of invalid type'''

        invalid_image_data = SimpleUploadedFile(
            'invalid_image.txt',
            b'INVALID_IMAGE_TEXT',
            content_type='text/plain'
        )
        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            {
                'profile_picture': invalid_image_data
            },
            format='multipart',
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['message'],
            'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
        )
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['type'],
            'invalid_image'
        )

    @override_settings(MAX_IMAGE_UPLOAD_SIZE=10)
    def test_update_image_image_too_large(self):
        '''Updating Profile Picture - Invalid :- When Image is Too large'''
        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            {
                'profile_picture': self._generate_fake_image(
                    'valid_image.png',
                    200,
                    (225, 120, 220)
                )
            },
            format='multipart')

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['message'],
            'Image size too large.'
        )
        self.assertEqual(
            response.data.get('errors').get('profile_picture')['type'],
            'invalid_image'
        )

    def test_update_image_user_invalid(self):
        '''Updating Profile Picture - Invalid :- When User does not exist (invalid uuid)'''

        image_data = SimpleUploadedFile(
            'valid_image.png',
            self.valid_image.getvalue()
        )
        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': 'averyRandomPassword'
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_update_image_user_not_exist(self):
        '''Updating Profile Picture - Invalid :- When User does not exist'''
        invalid_account = uuid.uuid4()

        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': invalid_account
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Accounts matches the given query.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    @patch('cloudinary.uploader.upload', side_effect=user_factory.CloudinaryMock.upload_fail)
    def test_update_image_cloudinary_server_down(self, mock_function):
        '''Updating Profile Picture - Invalid :-When There are issues with the cloudinary server'''
        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'An issue has occured with our cloudinary service.'
        )


class AccountsProfilePictureValid(AccountsProfilePicture):
    '''Handle Profile Picture Upload/Retrieve/Delete - When all valid'''

    def test_update_image_success(self):
        '''Updating Profile Picture - Valid: When the image is valid and uploaded'''
        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload.get('id'), self.user.id
        )
        self.assertEqual(
            payload.get('account').get('picture_url'), 'https://example.com/image_uploads/profiles/{}.png'.format(
                self.user.account.id
            )
        )
