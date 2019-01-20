from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import User, Permission, Group
from app.accounts.tests import factory as user_factory
from unittest.mock import patch


class TestCommands(TestCase):
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

    def tearDown(self):
        self.cloudinary_patcher.stop()
        self.cloudinary_upload_patcher.stop()
        self.user.delete()
        self.super_user.delete()

    def test_group_empty_before_command(self):
        '''Fix Permissions Command: Groups empty before  fix permissions management calls'''
        existing = Group.objects.all()
        self.assertEqual(existing.count(), 0)

    def test_fix_permissions_management_commands(self):
        '''Fix Permissions Command: Groups populated after fix permissions management calls'''

        # Create sample users
        call_command('fix-permissions')

        all_groups = Group.objects.all()
        self.assertEqual(all_groups.count(), 2)

    def test_upload_default_image_management_command(self):
        '''Upload Default Image Command: test cloudinary called'''

        call_command('upload-default-image')

        self.assertTrue(self.mock_cloudinary.called)
        self.assertTrue(self.mock_cloudinary_upload.called)
