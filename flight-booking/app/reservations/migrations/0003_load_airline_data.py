import os
import json
from django.conf import settings
from django.db import transaction, migrations, IntegrityError


def load_airline_data(apps, schema_editor):
    Airline = apps.get_model('reservations', 'Airline')
    db_alias = schema_editor.connection.alias

    data_location = os.path.join(
        settings.BASE_DIR,
        'app/reservations/files/airlines.json'
    )
    with open(data_location, encoding='utf-8') as file:
        airlines = json.load(file)
        with transaction.atomic():
            for code, airline_name in airlines.items():
                try:
                    Airline.objects.using(db_alias).create(
                        code=code,
                        airline_name=airline_name
                    )
                except IntegrityError:
                    continue


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_load_airport_data'),
    ]

    operations = [
        migrations.RunPython(load_airline_data),
    ]
