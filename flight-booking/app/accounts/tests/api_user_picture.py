from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch


class AccountsProfilePicture(APITestCase):
    def setUp(self):
        self.cloudinary_patcher = patch('cloudinary.utils.cloudinary_url')
        self.mock_cloudinary = self.cloudinary_patcher.start()

        self.user = User.objects.create_user(
            email='test@example.com', password='testuserpassword',
            username='testuser',
            first_name='example',
            last_name='demo'
        )

    def tearDown(self):
        self.cloudinary_patcher.stop()
        self.user.delete()


class AccountsProfilePictureExceptions(AccountsProfilePicture):
    '''Handle Profile Picture Upload/Retrieve/Delete - When not valid'''


class AccountsProfilePictureValid(AccountsProfilePicture):
    '''Handle Profile Picture Upload/Retrieve/Delete - When all valid'''
