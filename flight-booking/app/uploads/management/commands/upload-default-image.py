import cloudinary
import requests
import os
from django.core.management import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):

        default_image = cloudinary.utils.cloudinary_url('profiles/default.png')

        default_image_call = requests.head(default_image[0])

        if default_image_call.status_code == 404:
            # Upload stock image
            image_location = os.path.join(
                settings.BASE_DIR,
                'app/uploads/images/default.png'
            )

            cloudinary.uploader.upload(
                image_location,
                public_id='profiles/default'
            )

        return 'Default Profile Picture Set'

