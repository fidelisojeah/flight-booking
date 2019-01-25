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
from app.helpers import utils
from app.reservations.tests import factory as reservation_factory


class AirlineSchedule(APITestCase):
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
        self.single_flight_schedule = {
            'expected_departure': timezone.now() + timedelta(hours=2),
            'expected_arrival': timezone.now() + timedelta(hours=12),
            'departure_airport': 'JFK',
            'arrival_airport': 'ATL',
            'flight_number': '001a',
        }
        self.flight_schedule = {
            'period': 12,
            'time_of_flight': '17:00:00',
            'flight_duration': '6:00:00',
            'departure_airport': 'LHR',
            'arrival_airport': 'LOS',
            'flight_number': '007c',
        }

    def tearDown(self):
        self.user.delete()
        self.super_user.delete()


class AirlineScheduleExceptions(AirlineSchedule):
    '''Airline Schedule tests - Exceptions'''

    def test_list_airlines_no_permission(self):
        '''List/Filter Airlines - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'airlines-list',
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

    def test_filter_airline_schedule_no_permission(self):
        '''List/Filter Airline Flight Schedule - Invalid :- No permission (not logged in maybe)'''
        response = self.client.get(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WT'
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
    # Create Single Flight Schedule
    #
    def test_schedule_airline_single_flight_no_permission(self):
        '''Schedule Single Flight for Airline - Invalid :- No permission (not logged in maybe)'''
        flight_data = self.single_flight_schedule
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WT'
                }
            ),
            data=flight_data
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

    def test_schedule_airline_single_flight_bad_permission(self):
        '''Schedule Single Flight for Airline - Invalid :- When User does not have sufficient permission'''
        flight_data = self.single_flight_schedule
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WT'
                }
            ),
            data=flight_data,
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

    def test_schedule_airline_single_flight_missing_fields(self):
        '''Schedule Single Flight for Airline - Invalid :- When Not all fields are sent in'''
        flight_data = self.single_flight_schedule.copy()

        del flight_data['arrival_airport']
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WT'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['type'],
            'required'
        )

    def test_schedule_airline_single_flight_invalid_airline(self):
        '''Schedule Single Flight for Airline - Invalid :- When airline does not exist'''
        flight_data = self.single_flight_schedule.copy()

        del flight_data['departure_airport']
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WTA'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Airline matches the given query.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_schedule_airline_single_flight_when_departure_same_as_arrival(self):
        '''Schedule Single Flight for Airline - Invalid :- When Departure and Arrival are same airport'''
        flight_data = self.single_flight_schedule.copy()

        flight_data['departure_airport'] = flight_data['arrival_airport']
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'DL'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['message'],
            'Arrival airport cant be same as departure.'
        )
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['message'],
            'Arrival airport cant be same as departure.'
        )
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['type'],
            'invalid'
        )

    #
    # Create Daily Flight Schedule
    #
    def test_schedule_airline_daily_flights_no_permission(self):
        '''Create Daily Schedule Flight for Airline - Invalid :- No permission (not logged in maybe)'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=schedule_flight_data
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

    def test_schedule_airline_daily_flights_bad_permission(self):
        '''Create Daily Schedule Flight for Airline - Invalid :- When User does not have sufficient permission'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=schedule_flight_data,
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

    def test_schedule_airline_daily_flights_missing_fields(self):
        '''Create Daily Schedule Flight for Airline - Invalid :- When Not all fields are sent in'''
        flight_data = self.flight_schedule.copy()

        del flight_data['flight_number']
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'VS'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('flight_number')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('flight_number')['type'],
            'required'
        )

    def test_schedule_airline_daily_flights_invalid_airline(self):
        '''Create Daily Schedule Flight for Airline - Invalid :- When airline does not exist'''
        flight_data = self.flight_schedule.copy()

        del flight_data['departure_airport']
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BIH'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Airline matches the given query.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_schedule_airline_daily_flights_invalid_data_type(self):
        '''Create Daily Schedule Flight for Airline - Invalid :- When Flight duration is of invalid type'''
        flight_data = self.flight_schedule.copy()

        flight_data['flight_duration'] = 'USOSP'
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('flight_duration')['message'],
            'Duration has wrong format. Use one of these formats instead: [DD] [HH:[MM:]]ss[.uuuuuu].'
        )
        self.assertEqual(
            response.data.get('errors').get('flight_duration')['type'],
            'invalid'
        )

    def test_schedule_airline_daily_flights_when_departure_same_as_arrival(self):
        '''Schedule Single Flight for Airline - Invalid :- When Departure and Arrival are same airport'''
        flight_data = self.flight_schedule.copy()

        flight_data['departure_airport'] = flight_data['arrival_airport']
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'DL'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['message'],
            'Arrival airport cant be same as departure.'
        )
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['type'],
            'invalid'
        )
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['message'],
            'Arrival airport cant be same as departure.'
        )
        self.assertEqual(
            response.data.get('errors').get('arrival_airport')['type'],
            'invalid'
        )

    #
    # Create Weekly Flight Schedule
    #

    def test_schedule_airline_weekly_flights_no_permission(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- No permission (not logged in maybe)'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=schedule_flight_data
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

    def test_schedule_airline_weekly_flights_bad_permission(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- When User does not have sufficient permission'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=schedule_flight_data,
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

    def test_schedule_airline_weekly_flights_missing_fields(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- When Not all fields are sent in'''
        flight_data = self.flight_schedule.copy()

        del flight_data['period']
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'VA'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('period')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('period')['type'],
            'required'
        )

    def test_schedule_airline_weekly_flights_invalid_airline(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- When airline does not exist'''
        flight_data = self.flight_schedule.copy()

        del flight_data['time_of_flight']
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BIH'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'No Airline matches the given query.'
        )
        self.assertEqual(
            response.data.get('message'),
            'An error has occured.'
        )

    def test_schedule_airline_weekly_flights_invalid_departure_airport(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- When departure airport does not exist'''
        flight_data = self.flight_schedule.copy()

        flight_data['departure_airport'] = 'USOSP'
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['message'],
            'Invalid pk \"USOSP\" - object does not exist.'
        )
        self.assertEqual(
            response.data.get('errors').get('departure_airport')['type'],
            'does_not_exist'
        )

    def test_schedule_airline_weekly_flights_invalid_data_type(self):
        '''Create Weekly Schedule Flight for Airline - Invalid :- When Flight duration is of invalid type'''
        flight_data = self.flight_schedule.copy()

        flight_data['flight_duration'] = 'USOSP'
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('flight_duration')['message'],
            'Duration has wrong format. Use one of these formats instead: [DD] [HH:[MM:]]ss[.uuuuuu].'
        )
        self.assertEqual(
            response.data.get('errors').get('flight_duration')['type'],
            'invalid'
        )


class AirlineScheduleValid(AirlineSchedule):
    '''AirlineSchedule - Valid'''

    def test_filter_airlines(self):
        '''Filter list of all Airlines - Valid: No filters'''
        response = self.client.get(
            reverse(
                'airlines-list',
                kwargs={
                    'version': 'v1',
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertGreaterEqual(payload.get('count'), 1)

    def test_filter_airlines_filter_code(self):
        '''Filter list of all Airlines - Valid: filter Code'''
        response = self.client.get(
            reverse(
                'airlines-list',
                kwargs={
                    'version': 'v1',
                }
            ), data={
                'code': 'BA'
            },
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertEqual(payload.get('count'), 1)

        self.assertEqual(payload.get('results')[0].get(
            'airline_name'), 'British Airways')

    def test_filter_airlines_filter_name(self):
        '''Filter list of all Airlines - Valid: filter name'''
        response = self.client.get(
            reverse(
                'airlines-list',
                kwargs={
                    'version': 'v1',
                }
            ), data={
                'airline_name': 'Virgin'
            },
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertGreaterEqual(payload.get('count'), 1)

    def test_schedule_airline_single_flight(self):
        '''Schedule Single Flight for Airline - Valid :- When information provided okay'''
        flight_data = self.single_flight_schedule
        response = self.client.post(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'VS'
                }
            ),
            data=flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            payload.get('flight_designation'),
            'VS{}'.format(flight_data.get('flight_number'))
        )

        self.assertEqual(
            payload.get('departure_airport'), flight_data.get(
                'departure_airport')
        )
        self.assertEqual(
            payload.get('arrival_airport'), flight_data.get(
                'arrival_airport')
        )

    def test_schedule_airline_daily_flights(self):
        '''Create Daily Schedule Flight for Airline - Valid :- When Information Complete'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-daily-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'BA'
                }
            ),
            data=schedule_flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )

        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            payload[0].get('flight_designation'),
            'BA{}'.format(schedule_flight_data.get('flight_number'))
        )
        self.assertEqual(
            len(payload), schedule_flight_data.get('period')
        )
        self.assertEqual(
            payload[0].get('departure_airport'), schedule_flight_data.get(
                'departure_airport')
        )
        self.assertEqual(
            payload[0].get('arrival_airport'), schedule_flight_data.get(
                'arrival_airport')
        )

    def test_schedule_airline_weekly_flights(self):
        '''Create Weekly Schedule Flight for Airline - Valid :- When Information Complete'''
        schedule_flight_data = self.flight_schedule
        response = self.client.post(
            reverse(
                'airlines-weekly-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'DL'
                }
            ),
            data=schedule_flight_data,
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')

        self.assertTrue(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            payload[0].get('flight_designation'),
            'DL{}'.format(schedule_flight_data.get('flight_number'))
        )
        self.assertEqual(
            payload[0].get('departure_airport'), schedule_flight_data.get(
                'departure_airport')
        )
        self.assertEqual(
            payload[0].get('arrival_airport'), schedule_flight_data.get(
                'arrival_airport')
        )
        self.assertEqual(
            len(payload), schedule_flight_data.get('period')
        )

    def test_filter_airline_schedule(self):
        '''List/Filter Airline Flight Schedule - Valid'''
        reservation_factory.create_single_flight(airline='WT')
        response = self.client.get(
            reverse(
                'airlines-schedule',
                kwargs={
                    'version': 'v1',
                    'pk': 'WT'
                }
            ),
            HTTP_AUTHORIZATION=utils.generate_token(self.super_user)
        )
        payload = response.data.get('payload')
        self.assertTrue(response.data.get('success'))
        self.assertGreaterEqual(payload.get('count'), 1)
