import string
import random

from django.contrib.auth.models import User

from app.accounts.models import Accounts
from cloudinary import api as cloudinary_api


def create_user(*,
                email='test@example.com',
                password='testuserpassword',
                username='testuser',
                first_name='example',
                last_name='demo'
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

    account = Accounts.objects.create(
        user=user,
        profile_picture_public_id='profiles/default'
    )
    account.save()

    return user


class CloudinaryMock:
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
