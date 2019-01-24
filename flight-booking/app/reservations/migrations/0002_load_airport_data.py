import os
import json
from django.conf import settings
from django.db import transaction, migrations, IntegrityError


def _make_airport_dict(airport):

    fields = {
        'longitude': airport.get('lon', None),
        'airport_name': airport.get('name', None),
        'city': airport.get('city', None),
        'latitude': airport.get('lat', None),
        'country': airport.get('country', None),
        'code': airport.get('code', None)
    }
    return fields


def load_airport_data(apps, schema_editor):
    Airport = apps.get_model('reservations', 'Airport')
    db_alias = schema_editor.connection.alias

    data_location = os.path.join(
        settings.BASE_DIR,
        'app/reservations/files/airports.json'
    )
    with open(data_location, encoding='utf-8') as file:
        airports = json.load(file)
        with transaction.atomic():
            for airport in airports:
                try:
                    fields = _make_airport_dict(airport)

                    Airport.objects.using(db_alias).create(
                        **fields
                    )
                except IntegrityError:
                    continue


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_airport_data),
    ]
