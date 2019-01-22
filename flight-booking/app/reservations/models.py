import uuid

from django.db import models
from app.accounts import models as user_models
from rest_framework import (
    exceptions,
    status
)
from app.helpers import utils


class Airport(models.Model):
    '''Model containing Airport data'''
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    airport_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=5, primary_key=True)


class Airline(models.Model):
    '''Model containing Airline data'''
    code = models.CharField(max_length=5, primary_key=True)
    airline_name = models.CharField(max_length=255)

    class Meta:
        permissions = (
            ('view_flights', 'Can view flights by airline'),
            ('add_flights', 'Can create flights by airline'),
            ('change_flights', 'Can create flights by airline'),
            ('delete_flights', 'Can delete flights by airlines'),
        )


class Flight(models.Model):
    '''Model containing Flight data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    expected_departure = models.DateTimeField()
    expected_arrival = models.DateTimeField()

    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)

    departure_airport = models.ForeignKey(
        Airport,
        related_name='%(class)s_departure_flight',
        on_delete=models.CASCADE
    )
    arrival_airport = models.ForeignKey(
        Airport,
        related_name='%(class)s_arrival_flight',
        on_delete=models.CASCADE
    )
    airline = models.ForeignKey(
        Airline,
        related_name='%(class)s_airline',
        on_delete=models.CASCADE
    )
    flight_number = models.CharField(max_length=4)

    def get_flight_designation(self):
        return '{}{}'.format(self.airline.code, self.flight_number)

    def get_flight_duration(self):
        departure = self.expected_departure
        arrival = self.expected_arrival

        if hasattr(self, 'departure') and self.departure:
            departure = self.departure
        if hasattr(self, 'arrival') and self.arrival:
            arrival = self.arrival

        flight_duration = arrival - departure

        flight_hours, remainder = divmod(flight_duration.seconds, 3600)
        flight_minutes, _ = divmod(remainder, 60)

        return '{} Hour(s) {} Minute(s)'.format(flight_hours,
                                                flight_minutes)

    def save(self, *args, **kwargs):
        created_flight = Flight.objects.filter(
            airline=self.airline,
            flight_number=self.flight_number,
            expected_departure__contains=self.expected_departure.date(),
        )

        if not created_flight.exists():
            super(Flight, self).save(*args, **kwargs)


class Reservation(models.Model):
    '''Model containing Reservation data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    FIRST_CLASS = 0
    BUSINESS_CLASS = 1
    ECONOMY_CLASS = 2

    FLIGHT_CLASS = (
        (FIRST_CLASS, ('First Class')),
        (BUSINESS_CLASS, ('Business Class')),
        (ECONOMY_CLASS, ('Economy Class')),
    )

    flight_class = models.IntegerField(
        choices=FLIGHT_CLASS,
        default=ECONOMY_CLASS
    )

    author = models.ForeignKey(
        user_models.Accounts,
        null=False,
        blank=False,
        related_name='%(class)s_author',
        on_delete=models.CASCADE
    )
    first_flight = models.ForeignKey(
        Flight,
        null=False,
        blank=False,
        related_name='%(class)s_departure',
        on_delete=models.CASCADE
    )
    return_flight = models.ForeignKey(
        Flight,
        null=True,
        blank=True,
        related_name='%(class)s_return',
        on_delete=models.CASCADE
    )
    RETURN = 0
    ONE_WAY = 1

    TICKET_TYPE = (
        (RETURN, ('Return ticket')),
        (ONE_WAY, ('One way ticket'))
    )
    ticket_type = models.IntegerField(choices=TICKET_TYPE, default=ONE_WAY)

    class Meta:
        permissions = (
            ('update_own_reservation', 'Can Update His/Her reservations'),
            ('delete_own_reservation', 'Can remove His/Her reservations'),
            ('retrieve_own_reservations', 'Can View His/Her reservations'),

            ('create_any_reservation', 'Can Create reservations for any'),
            ('retrieve_any_reservations', 'Can View Any Users reservations'),
            ('update_any_reservations', 'Can Update Any Users reservations'),
            ('delete_any_reservations', 'Can remove Any Users reservations'),
        )

    def save(self, *args, **kwargs):

        if self.ticket_type == self.RETURN:
            if not (hasattr(self, 'return_flight') and self.return_flight):
                raise exceptions.ParseError(
                    'Return Tickets Must have Return Flights',
                )
            if self.return_flight == self.first_flight:
                raise utils.FieldErrorExceptions({
                    'return_flight': {
                        'message': 'Return Flight cannot be same as first flight.',
                        'code': 'invalid'
                    },
                    'first_flight': {
                        'message': 'Return Flight cannot be same as first flight.',
                        'code': 'invalid'
                    }
                })
            if self.return_flight.expected_arrival < self.first_flight.expected_departure:
                raise utils.FieldErrorExceptions({
                    'return_flight': {
                        'message': 'Return Flight cannot take off before First Flight lands.',
                        'code': 'invalid'
                    },
                    'first_flight': {
                        'message': 'Return Flight cannot take off before First Flight lands.',
                        'code': 'invalid'
                    }
                })
        else:
            self.return_flight = None

        super(Reservation, self).save(*args, **kwargs)
