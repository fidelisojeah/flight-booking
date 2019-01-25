from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.core.management import call_command
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from app.accounts.tests import factory as user_factory
from app.reservations.tests import factory as reservation_factory


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
        self.user1 = user_factory.create_user(
            email='testuser1@example.com',
            password='testuserpassword',
            username='testuser1',
            first_name='example',
            last_name='demo'
        )
        self.super_user = user_factory.create_user(
            email='admin@example.com',
            password='testuserpassword',
            username='admin',
            first_name='Admin',
            last_name='demo',
            user_type='super_staff'
        )
        self.staff = user_factory.create_user(
            email='staff@example.com',
            password='staffpassword',
            username='staffuser',
            first_name='Staff',
            last_name='User',
            user_type='staff'
        )

    def tearDown(self):
        self.cloudinary_patcher.stop()
        self.cloudinary_upload_patcher.stop()
        self.user.delete()
        self.staff.delete()
        self.super_user.delete()

    def test_group_empty_before_fix_permissions_command(self):
        '''Fix Permissions Command: Groups empty before  fix permissions management calls'''
        existing = Group.objects.all()
        self.assertEqual(existing.count(), 0)

    def test_fix_permissions_management_commands(self):
        '''Fix Permissions Command: Groups populated after fix permissions management calls'''

        # Create sample users
        call_command('fix-permissions')

        all_groups = Group.objects.all()
        self.assertEqual(all_groups.count(), 3)

    def test_upload_default_image_management_command(self):
        '''Upload Default Image Command: test cloudinary called'''

        call_command('upload-default-image')

        self.assertTrue(self.mock_cloudinary.called)
        self.assertTrue(self.mock_cloudinary_upload.called)

    def test_reservation_reminder_command_no_reservations(self):
        '''Reservation Reminder Mail - No reservations today'''
        command_return = call_command('reservation-reminders')

        self.assertEqual(command_return, 'Done! No Upcoming Reservations.')

    def test_reservation_reminder(self):
        '''Reservation Reminder Mail - Multiple Reservations'''
        flight = reservation_factory.create_single_flight(
            expected_departure=timezone.now()
        )

        reservation_factory.make_reservation_single(
            user_account=self.user,
            flight=flight,
        )
        reservation_factory.make_reservation_single(
            user_account=self.user1,
            flight=flight,
        )

        command_return = call_command('reservation-reminders')

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].from_email,
            'Flight Booking Reservations <reservartions@{}>'.format(
                settings.EMAIL_DOMAIN_URL))

        self.assertEqual(command_return, 'Done! All Reminder Emails sent.')
