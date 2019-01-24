from datetime import timedelta, datetime, date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction, models

from rest_framework import (
    generics,
    exceptions,
    pagination
)
from .serializers import (
    FlightSchedulerSerializer,
    FlightSerializer,
    ReservationSerializer,
    AirlineSerializer
)

from app.accounts.models import Accounts

from .models import(Flight, Airline, Reservation)


def _validate_schedule_details_(data, airline_code):
    '''Validate Schedule details (used by both daily and weekly)'''
    schedule_details = data.copy()

    schedule_serializer = FlightSchedulerSerializer(data=schedule_details)

    schedule_serializer.is_valid(raise_exception=True)

    return schedule_serializer.validated_data


def bulk_schedule_flight(requestor, *, period_type='days', airline_code, data):
    '''Bulk schedule regular flights (days or weeks)'''
    if not requestor.has_perm('reservations.add_flights'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    assert period_type == 'days' or period_type == 'weeks'

    airline = generics.get_object_or_404(Airline, pk=airline_code)

    validated_data = _validate_schedule_details_(data, airline_code)

    time_of_flight = validated_data.pop('time_of_flight')
    period = validated_data.pop('period')
    flight_duration = validated_data.pop('flight_duration')

    flight_schedule_time = timezone.now().replace(
        hour=time_of_flight.hour,
        minute=time_of_flight.minute,
        second=0
    )

    with transaction.atomic():
        for period_change in range(0, period):
            if period_type == 'days':
                period_change_weeks = 0
                period_change_days = period_change
            else:
                period_change_weeks = period_change
                period_change_days = 0

            expected_departure = flight_schedule_time + timedelta(
                weeks=period_change_weeks,
                days=period_change_days,
            )
            expected_arrival = expected_departure + flight_duration

            airline.flight_airline.create(
                **validated_data,
                expected_arrival=expected_arrival,
                expected_departure=expected_departure
            )
    flight_number = validated_data.get('flight_number')
    return FlightSerializer(
        airline.flight_airline,
        many=True).data


def schedule_flight(requestor, *, airline_code, data):
    '''Schedule single flight'''
    if not requestor.has_perm('reservations.add_flights'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    flight_details = data.copy()

    airline = generics.get_object_or_404(Airline, pk=airline_code)

    flight_details['airline'] = airline.code

    serializer = FlightSerializer(data=flight_details)

    serializer.is_valid(raise_exception=True)

    serializer.save()

    return serializer.data


def filter_flights(requestor, *, query_params):
    '''Filter available flights'''
    if not requestor.has_perm('reservations.view_flights'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    filter_date = query_params.get('date', None)
    filter_departure_location = query_params.get('from', None)
    filter_destination = query_params.get('destination', None)

    today = timezone.now()

    flights = Flight.objects.filter(
        expected_departure__gte=today
    )

    if filter_date is not None:
        if isinstance(filter_date, datetime):
            filter_date = filter_date.date()
        elif isinstance(filter_date, str):
            try:
                filter_date = parse(filter_date)
            except ValueError:
                pass
        if isinstance(filter_date, date):
            flights = flights.filter(
                expected_departure__contains=filter_date
            )
    if filter_departure_location is not None:
        flights = flights.filter(
            models.Q(
                departure_airport__city__contains=filter_departure_location
            ) | models.Q(
                departure_airport__country__contains=filter_departure_location
            ) | models.Q(
                departure_airport__airport_name__contains=filter_departure_location
            )
        )
    if filter_destination is not None:
        flights = flights.filter(
            models.Q(
                arrival_airport__city__contains=filter_destination
            ) | models.Q(
                arrival_airport__country__contains=filter_destination
            ) | models.Q(
                arrival_airport__airport_name__contains=filter_destination
            )
        )

    return FlightSerializer(
        flights,
        many=True).data


def retrieve_flight_for_airline(requestor, *, airline_code, query_params):
    '''Retrieve Flight Schedule for Airline'''
    if not requestor.has_perm('reservations.view_flights'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    airline = generics.get_object_or_404(Airline, pk=airline_code)

    flights = airline.flight_airline

    filter_date = query_params.get('date', None)
    filter_flight_number = query_params.get('flight_number', None)

    if filter_date is not None:
        if isinstance(filter_date, datetime.datetime):
            filter_date = filter_date.date()
        elif isinstance(filter_date, str):
            try:
                filter_date = parse(filter_date)
            except ValueError:
                pass
        if isinstance(filter_date, datetime.date):
            flights = flights.filter(
                expected_departure__contains=filter_date
            )
    if filter_flight_number is not None:
        flights = flights.filter(flight_number=filter_flight_number)

    return FlightSerializer(
        flights,
        many=True).data


def retrieve_flight(requestor, flight_pk):
    '''Retrieve Information about a flight'''
    if not requestor.has_perm('reservations.view_flight'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    flight = generics.get_object_or_404(Flight, pk=flight_pk)

    return FlightSerializer(flight).data


def make_reservation(requestor, *, account_pk, data):
    '''Make Flight Reservations'''
    # TODO: Ensure reservation is not in the past
    if requestor.has_perm('reservations.create_any_reservation'):
        pass
    elif requestor.has_perm('reservations.add_reservation'):
        if str(requestor.account.id) != str(account_pk):
            raise exceptions.PermissionDenied('Insufficient Permission.')
    else:
        raise exceptions.PermissionDenied('Insufficient Permission.')

    user_account = generics.get_object_or_404(Accounts, pk=account_pk)

    reservation_data = data.copy()

    reservation_data['author'] = user_account.id

    serializer = ReservationSerializer(
        data=reservation_data
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return serializer.data


def make_flight_reservation(requestor, *, flight_pk, data):
    '''Make Flight Reservations For self'''
    if not requestor.has_perm('reservations.add_reservation'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    account_pk = requestor.account.id

    reservation_data = data.copy()

    reservation_data['author'] = account_pk

    flight = generics.get_object_or_404(Flight, pk=flight_pk)

    reservation_data['first_flight'] = flight.id

    serializer = ReservationSerializer(
        data=reservation_data
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return serializer.data


def filter_reservations(requestor, query_params, *, account_pk=None):
    '''List and filter reservations'''
    reservations = Reservation.objects.filter(deleted_at=None)
    if requestor.has_perm('reservations.retrieve_any_reservations'):
        if account_pk is not None:
            reservations.filter(author=account_pk)
    elif requestor.has_perm('reservations.retrieve_own_reservations'):
        if account_pk is not None and account_pk != str(requestor.account.id):
            raise exceptions.PermissionDenied('Insufficient Permission.')

        reservations = reservations.filter(author=requestor.account.id)
    else:
        raise exceptions.PermissionDenied('Insufficient Permission.')

    filter_date = query_params.get('date', None)
    filter_flight_number = query_params.get('flight_number', None)

    if filter_flight_number is not None:
        reservations = reservations.filter(models.Q(
            first_flight__flight_number=filter_flight_number
        ) | models.Q(
            return_flight__flight_number=filter_flight_number
        ))

    if filter_date is not None:
        if isinstance(filter_date, datetime):
            filter_date = filter_date.date()
        elif isinstance(filter_date, str):
            try:
                filter_date = parse(filter_date)
            except ValueError:
                pass
    if isinstance(filter_date, date):
        reservations = reservations.filter(models.Q(
            first_flight__expected_departure__contains=filter_date
        ) | models.Q(
            return_flight__expected_departure__contains=filter_date
        ))

    # return ReservationSerializer(reservations, many=True).data
    return reservations


def filter_flight_reservations(requestor, flight_pk):
    if not requestor.has_perm('reservations.retrieve_any_reservations'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    flight = generics.get_object_or_404(Flight, pk=flight_pk)

    combined_reservations = flight.reservation_departure.order_by('first_flight').union(
        flight.reservation_return.order_by('return_flight'))

    return ReservationSerializer(combined_reservations, many=True).data


def make_own_reservation(requestor, *, data):
    '''Make Flight Reservations For self'''
    # TODO: Ensure reservation is not in the past
    if not requestor.has_perm('reservations.add_reservation'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    account_pk = requestor.account.id

    reservation_data = data.copy()

    reservation_data['author'] = account_pk

    serializer = ReservationSerializer(
        data=reservation_data
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return serializer.data


def filter_reservations_by_period(requestor, *, month, year, query_params, period):
    '''List and filter reservations by period'''
    reservations = Reservation.objects.filter(deleted_at=None)
    if requestor.has_perm('reservations.retrieve_any_reservations'):
        pass
    elif requestor.has_perm('reservations.retrieve_own_reservations'):
        reservations = Reservation.objects.filter(author=requestor.account.id)
    else:
        raise exceptions.PermissionDenied('Insufficient Permission.')

    start_range = parse('2019').replace(month=1, day=1)
    end_range = start_range + relativedelta(months=12) - timedelta(days=1)

    if period == 'month':
        if int(month) < 1 or int(month) > 12:
            raise exceptions.ParseError('Not a valid month.')

        start_range = start_range.replace(month=int(month), day=1)
        end_range = start_range + relativedelta(months=1) - timedelta(days=1)

    reservations = reservations.filter(models.Q(
        first_flight__expected_departure__range=[start_range, end_range]
    ) | models.Q(
        return_flight__expected_departure__range=[start_range, end_range]
    ))

    return reservations


def retrieve_reservation(requestor, *, reservation_pk, query_params):
    '''Retrieve single Reservation'''
    reservation = generics.get_object_or_404(Reservation, pk=reservation_pk)

    if requestor.has_perm('reservations.retrieve_any_reservations'):
        pass
    elif requestor.has_perm('reservations.retrieve_own_reservations'):
        if requestor.account.id != str(reservation.author.id):
            raise exceptions.NotFound()
    else:
        raise exceptions.PermissionDenied('Insufficient Permission.')

    return ReservationSerializer(reservation).data


def filter_airlines(requestor, query_params):
    '''Filter Airline Information'''
    if not requestor.has_perm('reservations.view_airline'):
        raise exceptions.PermissionDenied('Insufficient Permission.')

    airlines = Airline.objects.all()

    return airlines
