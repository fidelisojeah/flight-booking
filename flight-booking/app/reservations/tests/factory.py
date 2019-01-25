from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User


from app.reservations.models import Airline, Flight, Airport, Reservation
from app.accounts.models import Accounts


def create_single_flight(*,
                         airline='BA',
                         departure_airport='LHR',
                         arrival_airport='LOS',
                         expected_departure=(
                             timezone.now() + timedelta(hours=2)),
                         expected_arrival=(
                             timezone.now() + timedelta(hours=8)),
                         flight_number='001'
                         ):

    airline = Airline.objects.filter(code=airline)
    if not airline.exists():
        airline = Airline.objects.get(code='BA')
    else:
        airline = airline[0]

    departure_airport = Airport.objects.filter(code=departure_airport)
    if not departure_airport.exists():
        departure_airport = Airport.objects.get(code='LHR')
    else:
        departure_airport = departure_airport[0]

    arrival_airport = Airport.objects.filter(code=arrival_airport)
    if (not arrival_airport.exists()) or arrival_airport == departure_airport:
        arrival_airport = Airport.objects.get(code='LOS')
    else:
        arrival_airport = arrival_airport[0]

    flight = Flight.objects.create(
        arrival_airport=arrival_airport,
        departure_airport=departure_airport,
        expected_departure=expected_departure,
        expected_arrival=expected_arrival,
        flight_number=flight_number,
        airline=airline
    )

    flight.save()

    return flight


def create_return_flight(*,
                         first_flight_airline='BA',
                         first_flight_expected_departure=(
                             timezone.now() + timedelta(days=1, hours=2)),
                         first_flight_expected_arrival=(
                             timezone.now() + timedelta(days=1, hours=8)
                         ),
                         departure_airport='LHR',
                         arrival_airport='LOS',
                         return_flight_airline='BA',
                         return_flight_expected_departure=(
                             timezone.now() + timedelta(days=3, hours=2)
                         ),
                         return_flight_expected_arrival=(
                             timezone.now() + timedelta(days=3, hours=8)
                         ),
                         first_flight_number='0101',
                         return_flight_number='0401',
                         ):

    first_flight_airline = Airline.objects.filter(code=first_flight_airline)
    return_flight_airline = Airline.objects.filter(code=return_flight_airline)

    if not first_flight_airline.exists():
        first_flight_airline = Airline.objects.get(code='BA')
    else:
        first_flight_airline = first_flight_airline[0]

    if not return_flight_airline.exists():
        return_flight_airline = first_flight_airline
    else:
        return_flight_airline = return_flight_airline[0]

    first_flight_departure_airport = Airport.objects.filter(
        code=departure_airport
    )
    if not first_flight_departure_airport.exists():
        first_flight_departure_airport = Airport.objects.get(code='LHR')
    else:
        first_flight_departure_airport = first_flight_departure_airport[0]

    first_flight_arrival_airport = Airport.objects.filter(
        code=arrival_airport)

    if (not first_flight_arrival_airport.exists()) or first_flight_arrival_airport == departure_airport:
        first_flight_arrival_airport = Airport.objects.get(code='LOS')
    else:
        first_flight_arrival_airport = first_flight_arrival_airport[0]

    return_flight_arrival_airport = first_flight_departure_airport
    return_flight_departure_airport = first_flight_arrival_airport

    first_flight = Flight.objects.create(
        arrival_airport=first_flight_arrival_airport,
        departure_airport=first_flight_departure_airport,
        expected_departure=first_flight_expected_departure,
        expected_arrival=first_flight_expected_arrival,
        flight_number=first_flight_number,
        airline=first_flight_airline,
    )
    first_flight.save()

    return_flight = Flight.objects.create(
        arrival_airport=return_flight_arrival_airport,
        departure_airport=return_flight_departure_airport,
        expected_departure=return_flight_expected_departure,
        expected_arrival=return_flight_expected_arrival,
        flight_number=return_flight_number,
        airline=return_flight_airline,
    )
    return_flight.save()

    return first_flight, return_flight


def make_reservation_single(*,
                            user_account,
                            flight,
                            ):
    if isinstance(user_account, User):
        user_account = user_account.account

    reservation = Reservation.objects.create(
        author=user_account,
        first_flight=flight,
        ticket_type=Reservation.ONE_WAY,
    )
    reservation.save()
    return reservation


def make_reservation_return(*,
                            user_account,
                            first_flight,
                            return_flight,
                            ):
    reservation = Reservation.objects.create(
        author=user_account,
        first_flight=first_flight,
        return_flight=return_flight,
        ticket_type=Reservation.RETURN,

    )
    reservation.save()
    return reservation
