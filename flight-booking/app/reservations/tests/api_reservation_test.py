import uuid
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from django.test import override_settings, utils as django_utils

from app.accounts.tests import factory as user_factory

from app.reservations.tests.factory import (
    create_single_flight,
    create_return_flight,
    make_reservation_single,
    make_reservation_return
)

from app.helpers import utils
from app.reservations.models import (
    Reservation
)


class ReservationTests(APITestCase):
    def setUp(self):
        self.user = user_factory.create_user(
            email='test@example.com',
            password='testuserpassword',
            username='testuser',
            first_name='example',
            last_name='demo'
        )
        self.user1 = user_factory.create_user(
            email='test@example.co.uk',
            password='testuserpassword',
            username='testuser1',
            first_name='User',
            last_name='User1'
        )
        self.user2 = user_factory.create_user(
            email='test@demo.com',
            password='testuserpassword',
            username='testuser2',
            first_name='User',
            last_name='User2'
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
        self.flight1, self.flight2 = create_return_flight()

        self.return_ticket_reservation = make_reservation_return(
            user_account=self.user.account,
            first_flight=self.flight1,
            return_flight=self.flight2,
        )
        self.single_ticket_reservation = make_reservation_single(
            user_account=self.user1.account,
            flight=self.flight,
        )

        self.valid_reservation_data = {
            'first_flight': self.flight.id,
            'flight_class': Reservation.ECONOMY_CLASS,
            'ticket_type': Reservation.ONE_WAY,
        }
        self.valid_reservation_data_return = {
            'first_flight': self.flight1.id,
            'return_flight': self.flight2.id,
            'flight_class': Reservation.BUSINESS_CLASS,
            'ticket_type': Reservation.RETURN,
        }

    def tearDown(self):
        self.user.delete()
        self.super_user.delete()
        self.flight.delete()
        self.flight1.delete()
        self.flight2.delete()


class ReservationExceptions(ReservationTests):
    '''Reservations tests - Exceptions'''

    def test_list_flights_no_permission(self):
        '''List/Filter All Reservations - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'reservations-list',
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

    def test_list_flights_by_year_no_permission(self):
        '''List/Filter Reservations by Year- Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'reservations-filter-reservations-by-year',
                kwargs={
                    'version': 'v1',
                    'year': timezone.now().year
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

    def test_list_flights_by_month_no_permission(self):
        '''List/Filter Reservations by Month - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'reservations-filter-reservations-by-month',
                kwargs={
                    'version': 'v1',
                    'year': timezone.now().year,
                    'month': 1
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

    def test_list_flights_by_month_invalid_month(self):
        '''List/Filter Reservations by Month - Invalid :- Invalid Month'''
        response = self.client.get(
            reverse(
                'reservations-filter-reservations-by-month',
                kwargs={
                    'version': 'v1',
                    'year': timezone.now().year,
                    'month': 26
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Not a valid month.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_retrieve_reservation_no_permission(self):
        '''Retrieve Single Reservation - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'reservations-detail',
                kwargs={
                    'version': 'v1',
                    'pk': self.single_ticket_reservation.id
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

    def test_retrieve_reservation_not_for_user(self):
        '''Retrieve Single Reservation - Invalid :- Bad permission'''
        response = self.client.get(
            reverse(
                'reservations-detail',
                kwargs={
                    'version': 'v1',
                    'pk': self.single_ticket_reservation.id
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user2)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    #
    # Create Reservation
    #
    def test_make_reservation_no_permission(self):
        '''Make Reservation For self - Invalid :- No permission (not logged in maybe)'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_bad_permission(self):
        '''Make Reservation For self - Invalid :- When User does not have sufficient permission'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_missing_fields(self):
        '''Make Reservation For self - Invalid :- When Not all fields are sent in'''
        reservation_data = self.valid_reservation_data_return.copy()

        del reservation_data['return_flight']
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_flight_not_exist(self):
        '''Make Reservation For self - Invalid :- When Flight does not exist'''
        reservation_data = self.valid_reservation_data.copy()
        del reservation_data['first_flight']
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_when_return_same_as_first_flight(self):
        '''Make Reservation For self - Invalid :- When Return Flight same as First Flight'''
        reservation_data = self.valid_reservation_data_return.copy()

        reservation_data['return_flight'] = reservation_data['first_flight']
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_when_return_flight_before_first(self):
        '''Make Reservation For self - Invalid :- When Return Flight Takes off before First Flight Lands'''
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
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_make_reservation_when_return_airport_different(self):
        '''Make Reservation For self - Invalid :- When Return Flight Lands in different city'''
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
                'reservations-list',
                kwargs={
                    'version': 'v1',
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


class ReservationValid(ReservationTests):
    '''Reservations tests - Valid'''

    def test_make_reservation(self):
        '''Make Reservation For self - Valid :- When Information is Valid'''
        reservation_data = self.valid_reservation_data
        response = self.client.post(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
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

    def test_list_reservations(self):
        '''List/Filter All Reservations - Valid :- Payload correct'''
        response = self.client.get(
            reverse(
                'reservations-list',
                kwargs={
                    'version': 'v1',
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )

        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            payload.get('count'), 2
        )
        self.assertEqual(
            len(payload.get('results')), 2
        )

    def test_list_reservations_by_year(self):
        '''List/Filter Reservations by Year- Valid :- Payload correct'''
        response = self.client.get(
            reverse(
                'reservations-filter-reservations-by-year',
                kwargs={
                    'version': 'v1',
                    'year': timezone.now().year
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )

        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reservations_by_month(self):
        '''List/Filter Reservations by Month - Valid :- Payload correct'''
        response = self.client.get(
            reverse(
                'reservations-filter-reservations-by-month',
                kwargs={
                    'version': 'v1',
                    'year': timezone.now().year,
                    'month': timezone.now().month
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )

        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @django_utils.override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('app.reservations.tasks.send_reservation_information.delay')
    def test_retrieve_reservation_by_email(self, mock_celery):
        '''Retrieve Reservation by Email - Valid : payload correct'''
        response = self.client.get(
            reverse(
                'reservations-send-reservation-email',
                kwargs={
                    'version': 'v1',
                    'pk': self.single_ticket_reservation.id,
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user1)
        )
        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Email Sent!.')
        self.assertEqual(payload.get('flight_class'),
                         self.single_ticket_reservation.flight_class)

        self.assertTrue(mock_celery.assert_called_once, 1)

    def test_retrieve_reservation(self):
        '''Retrieve Reservation - Valid : payload correct'''
        response = self.client.get(
            reverse(
                'reservations-detail',
                kwargs={
                    'version': 'v1',
                    'pk': self.return_ticket_reservation.id,
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload.get('flight_class'),
                         self.return_ticket_reservation.flight_class)
