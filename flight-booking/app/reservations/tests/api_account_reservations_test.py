import uuid
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from django.test import override_settings, utils as django_utils

from app.helpers import utils
from app.accounts.tests import factory as user_factory
from app.reservations.tests.factory import create_single_flight
from app.reservations.models import (
    Reservation
)


class AccountReservation(APITestCase):
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
        self.flight = create_single_flight()
        self.valid_reservation_data = {
            'first_flight': self.flight.id,
            'flight_class': Reservation.BUSINESS_CLASS,
            'ticket_type': Reservation.ONE_WAY,
        }

    def tearDown(self):
        self.user.delete()
        self.super_user.delete()
        self.flight.delete()


class AccountReservationExceptions(AccountReservation):
    '''Airline Schedule tests - Exceptions'''

    def test_list_airlines_no_permission(self):
        '''List/Filter Own Reservations - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
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

    def test_list_airlines_bad_permission(self):
        '''List/Filter Own Reservations - Invalid :- Insufficient Permissions'''
        response = self.client.get(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
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
    # Make Single Reservation for Account
    #
    def test_book_single_flight_for_user_no_permission(self):
        '''Book Flight for User Account - Invalid :- No permission (not logged in maybe)'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id,
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

    def test_book_single_flight_for_user_bad_permission(self):
        '''Book Flight for User Account - Invalid :- When User does not have sufficient permission'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.super_user.account.id,
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
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

    def test_book_single_flight_for_user_missing_fields(self):
        '''Book Flight for User Account - Invalid :- When Not all fields are sent in'''
        reservation_data = self.valid_reservation_data.copy()

        del reservation_data['first_flight']
        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id,
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('first_flight')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['type'],
            'required'
        )

    def test_book_single_flight_for_user_invalid_user_account(self):
        '''Book Flight for User Account - Invalid :- When Account Invalid'''
        reservation_data = self.valid_reservation_data.copy()

        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': 'WTA'
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_book_single_flight_for_user_user_not_exist(self):
        '''Book Flight for User Account - Invalid :- When user does not exist'''
        reservation_data = self.valid_reservation_data.copy()
        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': uuid.uuid4()
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Accounts matches the given query.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_book_single_flight_for_user_when_return_flight_same_as_first(self):
        '''Book Flight for User Account - Invalid :- When First and Return Flights are same'''
        reservation_data = self.valid_reservation_data.copy()

        reservation_data['return_flight'] = reservation_data['first_flight']
        reservation_data['ticket_type'] = Reservation.RETURN

        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('return_flight')['message'],
            'Return Flight cannot be same as first flight.',
        )
        self.assertEqual(
            response.data.get('errors').get('return_flight')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['message'],
            'Return Flight cannot be same as first flight.',
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['type'],
            'invalid'
        )

    def test_book_single_flight_for_user_when_return_flight_before_first(self):
        '''Book Flight for User Account - Invalid :- When Return Flight Takes off before First Flight Lands'''
        reservation_data = self.valid_reservation_data.copy()

        return_flight = create_single_flight(
            flight_number='0036',
            departure_airport='LOS',
            arrival_airport='LHR',
            expected_arrival=timezone.now() + timedelta(hours=12),
            expected_departure=timezone.now() + timedelta(hours=6)
        )

        reservation_data['return_flight'] = return_flight.id
        reservation_data['ticket_type'] = Reservation.RETURN

        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('return_flight')['message'],
            'Return Flight cannot take off before First Flight lands.',
        )
        self.assertEqual(
            response.data.get('errors').get('return_flight')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['message'],
            'Return Flight cannot take off before First Flight lands.',
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['type'],
            'invalid'
        )

    def test_book_single_flight_for_user_when_return_airport_different(self):
        '''Book Flight for User Account - Invalid :- When Return Flight Lands in different city'''
        reservation_data = self.valid_reservation_data.copy()

        return_flight = create_single_flight(
            flight_number='0192',
            departure_airport='LOS',
            arrival_airport='JFK',
            expected_departure=timezone.now() + timedelta(days=1),
            expected_arrival=timezone.now() + timedelta(days=1, hours=12)
        )

        reservation_data['return_flight'] = return_flight.id
        reservation_data['ticket_type'] = Reservation.RETURN

        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('return_flight')['message'],
            'Return Flight must land in same city as first flight.',
        )
        self.assertEqual(
            response.data.get('errors').get('return_flight')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['message'],
            'Return Flight must land in same city as first flight.',
        )
        self.assertEqual(
            response.data.get('errors').get('first_flight')['type'],
            'invalid'
        )


class AccountReservationValid(AccountReservation):
    '''Make reservations By account'''

    def test_book_single_flight_for_user(self):
        '''Book Flight for User Account - Valid :- '''
        reservation_data = self.valid_reservation_data.copy()

        response = self.client.post(
            reverse(
                'account-reservations-reservations',
                kwargs={
                    'version': 'v1',
                    'pk': self.user.account.id,
                }
            ),
            data=reservation_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
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
