import uuid
from django.contrib.auth.models import User
from django.db import models

from app.uploads.services import default_pic_details


class Accounts(models.Model):
    ''' Model containing basic User Information '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    CLIENT = 0
    STAFF = 1
    SUPER_STAFF = 2

    USER_TYPES = (
        (CLIENT, 'Client'),
        (STAFF, 'Normal Staff'),
        (SUPER_STAFF, 'Super Staff'),
    )

    user = models.OneToOneField(
        User,
        null=False,
        blank=False,
        related_name='account',
        on_delete=models.CASCADE,
    )
    profile_picture_url = models.TextField(default='')
    profile_picture_public_id = models.TextField(default='')

    user_type = models.IntegerField(default=CLIENT, choices=USER_TYPES)
    passport_number = models.CharField(max_length=255, blank=True, null=True)

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

    def get_full_name(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)
