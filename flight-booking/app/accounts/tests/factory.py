import string
import random

from django.contrib.auth.models import User, Permission

from app.accounts.models import Accounts
from cloudinary import api as cloudinary_api

from app.accounts.permissions import GROUPS


def create_user(*,
                email='test@example.com',
                password='testuserpassword',
                username='testuser',
                first_name='example',
                last_name='demo',
                user_type='client',
                ):
    ''' Create A user (For testing)'''
    user = User(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name
    )

    user.set_password(password)

    user.save()

    user = fix_user_permissions(user, user_type)

    account_user_type = Accounts.CLIENT
    if user_type == 'staff':
        account_user_type = Accounts.STAFF
    if user_type == 'super_staff':
        account_user_type = Accounts.SUPER_STAFF

    account = Accounts.objects.create(
        user=user,
        profile_picture_public_id='profiles/default',
        user_type=account_user_type
    )
    account.save()

    return user


def fix_user_permissions(user, user_type):
    user_group = GROUPS.get(user_type, None)
    if user_group is None:
        return

    for model, permission in user_group:
        try:
            user.user_permissions.add(
                Permission.objects.get(codename=permission)
            )
        except Permission.DoesNotExist:
            pass
    return user


class CloudinaryMock:
    def cloudinary_url(public_id, **options):
        '''Mock Cloudinary url util'''
        if options.pop('secure', None) is not None:
            options['secure'] = 'https://example.com/image_uploads/{}'.format(
                public_id)

        normal_url = 'http://example.com/image_uploads/{}'.format(
            public_id)
        return normal_url, options

    def upload(file, **options):
        '''Cloudinary upload mock'''
        public_id = options.get('public_id', 'default').replace(" ", "-")

        if public_id.endswith('/'):
            public_id += ''.join(random.choices(string.ascii_lowercase, k=6))

        secure_url = 'https://example.com/image_uploads/{}.png'.format(
            public_id)

        return {
            'secure_url': secure_url,
            'url': 'http://example.com/image_uploads/{}.png'.format(public_id)
        }

    def upload_fail(file, **options):
        '''Cloudinary upload mock SERVER ERROR'''
        raise cloudinary_api.Error('Bad Network Connection')
