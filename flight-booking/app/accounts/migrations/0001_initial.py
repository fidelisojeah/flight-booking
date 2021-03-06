# Generated by Django 2.1.5 on 2019-01-19 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('profile_picture_url', models.TextField(default='')),
                ('profile_picture_public_id', models.TextField(default='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('update_own_picture', 'Can Update His/Her Profile Picture'), ('delete_own_picture', 'Can remove His/Her Profile Picture'), ('retrieve_own_picture', 'Can View His/Her Profile Picture'), ('retrieve_any_picture', 'Can View Any Profile Picture'), ('update_any_picture', 'Can Update Any Users Profile Picture'), ('delete_any_picture', 'Can remove Any Users Profile Picture')),
            },
        ),
    ]
