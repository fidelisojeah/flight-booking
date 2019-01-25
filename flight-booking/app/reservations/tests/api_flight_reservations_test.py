import uuid
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from django.test import override_settings, utils as django_utils

from app.accounts.tests import factory as user_factory

from app.reservations.tests.factory import create_return_flight, make_reservation_single

from app.helpers import utils
from app.reservations.models import (
    Reservation
)


class FlightReservation(APITestCase):
    def setUp(self):
        self.user = user_factory.create_user(
            email='test@example.com',
            password='testuserpassword',
            username='testuser',
            first_name='example',
            last_name='demo'
        )
        self.super_user = user_factory.create_user(
            email='adminuser@example.com',
            password='adminuserpassword',
            username='adminuser',
            first_name='Admin',
            last_name='User',
            user_type='super_staff'
        )

        self.flight, self.flight2 = create_return_flight()
        self.valid_reservation_data = {
            'return_flight': self.flight2.id,
            'flight_class': Reservation.BUSINESS_CLASS,
            'ticket_type': Reservation.RETURN,
        }

    def tearDown(self):
        self.user.delete()
        self.super_user.delete()
        self.flight.delete()
        self.flight2.delete()


class FlightReservationExceptions(FlightReservation):
    '''Flight Reservations tests - Exceptions'''

    def test_list_flights_no_permission(self):
        '''List/Filter Flights - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'flights-list',
                kwargs={
                    'version': 'v1',
                }
            )
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_retrieve_flight_no_permission(self):
        '''Retrieve Single Flight - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'flights-detail',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            )
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    #
    # Create Single Flight Reservation
    #
    def test_make_reservation_for_flight_no_permission(self):
        '''Make Reservation for Flight - Invalid :- No permission (not logged in maybe)'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            ),
            data=reservation_data
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_make_reservation_for_flight_bad_permission(self):
        '''Make Reservation for Flight - Invalid :- When User does not have sufficient permission'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Insufficient Permission.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_make_reservation_for_flight_missing_fields(self):
        '''Make Reservation for Flight - Invalid :- When Not all fields are sent in'''
        reservation_data = self.valid_reservation_data.copy()

        del reservation_data['return_flight']
        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('return_flight')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('return_flight')['type'],
            'required'
        )

    def test_make_reservation_for_flight_invalid_flight(self):
        '''Make Reservation for Flight - Invalid :-  When Flight pk is of invalid type'''
        reservation_data = self.valid_reservation_data.copy()

        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': 'WTA'
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_make_reservation_for_flight__flight_not_exist(self):
        '''Make Reservation for Flight - Invalid :- When Flight does not exist'''
        reservation_data = self.valid_reservation_data.copy()

        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': uuid.uuid4()
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Flight matches the given query.'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_make_reservation_for_flight_when_return_same_as_first_flight(self):
        '''Make Reservation for Flight - Invalid :- When Return Flight same as First Flight'''
        reservation_data = self.valid_reservation_data.copy()

        reservation_data['return_flight'] = self.flight.id
        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('return_flight')['message'],
            'Return Flight cannot be same as first flight.'
        )
        self.assertEqual(
            response.data.get('errors').get('return_flight')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['message'],
            'Return Flight cannot be same as first flight.'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['type'],
            'invalid'
        )


class FlightReservationValid(FlightReservation):
    '''When Calls are valid'''

    def test_list_flights_no_query_params(self):
        '''List/Filter Flights - Valid :- No filter'''
        response = self.client.get(
            reverse(
                'flights-list',
                kwargs={
                    'version': 'v1',
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)

        )
        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(payload), 2
        )

    def test_list_flights_filter_dates(self):
        '''List/Filter Flights - Valid :-Filter by Dates'''
        response = self.client.get(
            reverse(
                'flights-list',
                kwargs={
                    'version': 'v1',
                }
            ),
            data={
                'date': timezone.now() + timedelta(days=1)
            },
            HTTP_AUTHORIZATION=utils.generate_token(self.user)

        )
        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(payload), 2
        )

    def test_make_reservation_for_flight_no_permission(self):
        '''Make Reservation for Flight - Invalid :- No permission (not logged in maybe)'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'flights-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.flight.id
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user),
            data=reservation_data
        )
        self.assertTrue(response.data.get('success'))

        payload = response.data.get('payload')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            payload.get('flight_class'), reservation_data.get('flight_class')
        )
        self.assertEqual(
            payload.get('reserved_by').get('full_name'),
            '{} {}'.format(self.user.first_name, self.user.last_name)
        )
        self.assertEqual(
            response.data.get('message'),
            'Reservation made Successfully.'
        )
