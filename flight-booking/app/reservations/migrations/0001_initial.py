# Generated by Django 2.1.5 on 2019-01-22 22:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0004_accounts_passport_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('airline_name', models.CharField(max_length=255)),
            ],
            options={
                'permissions': (('view_flights', 'Can view flights by airline'), ('add_flights', 'Can create flights by airline'), ('change_flights', 'Can create flights by airline'), ('delete_flights', 'Can delete flights by airlines')),
            },
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('airport_name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expected_departure', models.DateTimeField()),
                ('expected_arrival', models.DateTimeField()),
                ('departure', models.DateTimeField(blank=True, null=True)),
                ('arrival', models.DateTimeField(blank=True, null=True)),
                ('flight_number', models.CharField(max_length=4)),
                ('airline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_airline', to='reservations.Airline')),
                ('arrival_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_arrival_flight', to='reservations.Airport')),
                ('departure_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_departure_flight', to='reservations.Airport')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('flight_class', models.IntegerField(choices=[(0, 'First Class'), (1, 'Business Class'), (2, 'Economy Class')], default=2)),
                ('ticket_type', models.IntegerField(choices=[(0, 'Return ticket'), (1, 'One way ticket')], default=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservation_author', to='accounts.Accounts')),
                ('first_flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservation_departure', to='reservations.Flight')),
                ('return_flight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservation_return', to='reservations.Flight')),
            ],
            options={
                'permissions': (('update_own_reservation', 'Can Update His/Her reservations'), ('delete_own_reservation', 'Can remove His/Her reservations'), ('retrieve_own_reservations', 'Can View His/Her reservations'), ('create_any_reservation', 'Can Create reservations for any'), ('retrieve_any_reservations', 'Can View Any Users reservations'), ('update_any_reservations', 'Can Update Any Users reservations'), ('delete_any_reservations', 'Can remove Any Users reservations')),
            },
        ),
    ]
