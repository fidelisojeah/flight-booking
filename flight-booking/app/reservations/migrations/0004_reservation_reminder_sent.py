# Generated by Django 2.1.5 on 2019-01-24 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_load_airline_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
    ]
