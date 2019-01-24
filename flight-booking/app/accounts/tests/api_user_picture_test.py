import uuid
from PIL import Image
from io import BytesIO

from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, utils as django_utils

from app.accounts.tests import factory as user_factory
from app.helpers import utils


class AccountsProfilePicture(APITestCase):
    def setUp(self):
        self.cloudinary_patcher = patch(
            'cloudinary.utils.cloudinary_url',
            side_effect=user_factory.CloudinaryMock.cloudinary_url
        )
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
        self.super_user = user_factory.create_user(
            email='adminuser@example.com',
            password='adminuserpassword',
            username='adminuser',
            first_name='Admin',
            last_name='User',
            user_type='super_staff'
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
        self.super_user.delete()


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
            format='multipart',
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )

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
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
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
            format='multipart',
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )

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
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)

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
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
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

    def test_update_image_user_bad_permissions(self):
        '''Updating Profile Picture - Invalid :- When User does not have sufficient permission (update any)'''

        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_update_image_user_no_permissions(self):
        '''Updating Profile Picture - Invalid :- No permission (not logged in maybe)'''

        response = self.client.put(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id
                }),
            {
                'profile_picture': self._generate_fake_image('valid_image.png')
            },
            format='multipart',
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
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
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'An issue has occured with our cloudinary service.'
        )

    def test_delete_profile_image_user_invalid(self):
        '''Deleting Profile Picture - Invalid :- When User does not exist (invalid uuid)'''
        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': 'averyRandomPassword'
                }),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_delete_profile_image_user_not_exist(self):
        '''Deleting Profile Picture - Invalid :- When User does not exist'''
        invalid_account = uuid.uuid4()

        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': invalid_account
                }),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
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

    def test_delete_profile_image_bad_permissions(self):
        '''Deleting Profile Picture - Invalid :- When User does not have sufficient permission (update any)'''

        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id
                }),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_delete_profile_image_no_permissions(self):
        '''Deleting Profile Picture - Invalid :- When No permission (not logged in)'''

        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id
                }),
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
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
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
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

    def test_delete_profile_image_success_no_previous_upload(self):
        '''Deleting Profile Picture - Valid: When user had no previous profile picture'''
        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload.get('id'), self.user.id
        )
        self.assertEqual(
            payload.get('account').get('picture_url'), 'http://example.com/image_uploads/profiles/default.png')

    @django_utils.override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('app.uploads.tasks.remove_profile_picture.delay')
    def test_delete_profile_image_success(self, remove_profile_picture):
        '''Deleting Profile Picture - Valid: When user had previous profile picture'''
        result = self.client.put(
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
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        response = self.client.delete(
            reverse(
                'accounts-handle-profile-picture',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload.get('id'), self.user.id
        )
        self.assertEqual(
            payload.get('account').get('picture_url'), 'http://example.com/image_uploads/profiles/default.png')
