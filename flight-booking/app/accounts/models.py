import uuid
from django.contrib.auth.models import User
from django.db import models

from app.uploads.services import default_pic_details


class Accounts(models.Model):
    ''' Model containing basic User Information '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        null=False,
        blank=False,
        related_name='%(class)s_account',
        on_delete=models.CASCADE,
    )
    profile_picture_url = models.TextField(default='')
    profile_picture_public_id = models.TextField(default='')

    class Meta:
        permissions = (
            ('update_own_picture', 'Can Update His/Her Profile Picture'),
            ('delete_own_picture', 'Can remove His/Her Profile Picture'),
            ('retrieve_own_picture', 'Can View His/Her Profile Picture'),
            ('retrieve_any_picture', 'Can View Any Profile Picture'),
            ('update_any_picture', 'Can Update Any Users Profile Picture'),
            ('delete_any_picture', 'Can remove Any Users Profile Picture'),
        )

    def get_profile_picture_url(self):
        if not self.profile_picture_url or self.profile_picture_public_id == 'profiles/default':
            return default_pic_details()
        return self.profile_picture_url
