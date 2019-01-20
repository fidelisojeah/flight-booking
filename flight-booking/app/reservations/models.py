import uuid

from django.db import models
from app.accounts import models as user_models


class Airport(models.Model):
    '''Model containing Airport data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    airport_name = models.CharField()
    city = models.CharField()
    country = models.CharField()
    code = models.CharField()


class Airline(models.Model):
    '''Model containing Airline data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField()
    airline_name = models.CharField()


class Flight(models.Model):
    '''Model containing Flight data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    FIRST_CLASS = 0
    BUSINESS_CLASS = 1
    ECONOMY_CLASS = 2

    FLIGHT_TYPE = (
        (FIRST_CLASS, ('First Class')),
        (BUSINESS_CLASS, ('Business Class')),
        (ECONOMY_CLASS, ('Economy Class')),
    )

    flight_type = models.IntegerField(
        choices=FLIGHT_TYPE,
        default=ECONOMY_CLASS
    )

    expected_departure = models.DateTimeField()
    expected_arrival = models.DateTimeField()

    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)

    airport = models.ForeignKey(Airport, related_name='%(class)s_flight',
                                on_delete=models.CASCADE
                                )
    airline = models.ForeignKey(Airline, related_name='%(class)s_flight',
                                on_delete=models.CASCADE

                                )

    # flight_number =
    def get_flight_duration(self):
        departure = self.expected_departure
        arrival = self.expected_arrival
        if hasattr(self, 'departure'):
            departure = self.departure
        if hasattr(self, 'arrival'):
            arrival = self.arrival

        return (arrival - departure).total_seconds()


class Reservation(models.Model):
    '''Model containing Reservation data'''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default='')

    author = models.ForeignKey(
        user_models.Accounts,
        null=False,
        blank=False,
        related_name='%(class)s_reservation',
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
        (ONE_WAY, ('One way'))
    )
    ticket_type = models.IntegerField(choices=TICKET_TYPE, default=RETURN)
