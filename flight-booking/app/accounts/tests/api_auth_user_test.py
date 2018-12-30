from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch


class AuthTest(APITestCase):
    def setUp(self):
        self.cloudinary_patcher = patch('cloudinary')
        self.mock_cloudinary = self.cloudinary_patcher.start()

        self.user = User.objects.create_user(
            email='test@example.com', password='testuserpassword',
            username='testuser',
            first_name='example',
            last_name='demo'
        )
        self.valid_data = {
            'username': 'testuser',
            'password': 'testuserpassword'
        }

    def tearDown(self):
        self.cloudinary_patcher.stop()
        self.user.delete()


class AuthTestExceptions(AuthTest):
    '''Authenticates a new User - When not valid'''

    def test_auth_user_username_not_sent(self):
        '''Authenticate a User - Invalid :- When the username not passed'''
        data = self.valid_data.copy()

        data.pop('username')

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'This field can not be left blank.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'required'
        )

    def test_auth_user_password_not_sent(self):
        '''Authenticate a User - Invalid :- When the password not passed'''
        data = self.valid_data.copy()

        data.pop('password')

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'This field can not be left blank.'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'required'
        )

    def test_auth_user_multiple_fields_not_sent(self):
        '''Authenticate a User - Invalid :- When the password not passed'''
        data = self.valid_data.copy()

        data.pop('username')

        data.pop('password')

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'This field can not be left blank.'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'required'
        )

        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'This field can not be left blank.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'required'
        )

    def test_auth_user_username_incorrect(self):
        '''
        Authenticate a User - Invalid :-
        When the username or email sent is invalid
        '''
        data = self.valid_data.copy()

        data['username'] = 'invalid'

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Unable to log in with provided credentials.'
        )

    def test_auth_user_password_incorrect(self):
        '''
        Authenticate a User - Invalid :-
        When the password sent is invalid
        '''
        data = self.valid_data.copy()

        data['password'] = 'invalid'

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Unable to log in with provided credentials.'
        )
        self.assertEqual(response.data.get('message'), 'An error has occured.')

    def test_auth_user_username_and_password_incorrect(self):
        '''
        Authenticate a User - Invalid :-
        When the username/email and password are invalid
        '''
        data = self.valid_data.copy()

        data['username'] = 'invalid'
        data['password'] = 'invalid'

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get('errors').get('global'),
            'Unable to log in with provided credentials.'
        )
        self.assertEqual(response.data.get('message'), 'An error has occured.')


class AuthTestValid(AuthTest):
    '''Authenticate a User - VALID :- When data is valid'''

    def test_auth_user_username(self):
        '''
        Authenticate a User - VALID :- When a valid username is used to sign in
        '''
        data = self.valid_data.copy()

        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'Sign in Successful.'
        )
        self.assertFalse('errors' in response.data)
        self.assertNotContains(response, 'password',
                               status_code=status.HTTP_200_OK)
        self.assertContains(response, 'token', status_code=status.HTTP_200_OK)
        self.assertContains(response, 'user', status_code=status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('payload')['user']['username'],
            data['username']
        )

    def test_auth_user_valid_email_as_username(self):
        '''
        Authenticate a User - VALID :-
        When a valid email as username is used to sign in
        '''
        data = self.valid_data.copy()
        data['username'] = self.user.email
        response = self.client.post(
            reverse('accounts-auth-user', kwargs={"version": "v1"}),
            data
        )

        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('message'),
            'Sign in Successful.'
        )
        self.assertFalse('errors' in response.data)

        self.assertNotContains(
            response,
            'password',
            status_code=status.HTTP_200_OK)

        self.assertContains(response, 'token', status_code=status.HTTP_200_OK)
        self.assertContains(response, 'user', status_code=status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('payload')['user']['username'],
            self.user.username
        )
