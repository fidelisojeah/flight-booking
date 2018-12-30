from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch


class AccountsTest(APITestCase):
    def setUp(self):
        self.cloudinary_patcher = patch('cloudinary.utils.cloudinary_url')
        self.mock_cloudinary = self.cloudinary_patcher.start()

        self.initial_user = User.objects.create_user(
            'testuser', 'test@example.com', 'testuserpassword'
        )
        self.valid_data = {
            'username': 'seconduser',
            'first_name': 'Example',
            'last_name': 'User',
            'email': 'seconduser@example.com',
            'password': 'SecondUserValidatedPassword123$@46'
        }

    def tearDown(self):
        self.cloudinary_patcher.stop()


class AccountsTestExceptions(AccountsTest):
    '''Create a new User - When not valid'''

    def test_create_user_email_not_sent(self):
        '''Create a new User - Invalid :- When the email not passed'''
        data = self.valid_data.copy()

        data.pop('email')

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('email')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['type'],
            'required'
        )
        self.assertFalse(response.data.get('success'))

    def test_create_user_username_not_sent(self):
        '''Create a new User - Invalid :- When the username not passed'''
        data = self.valid_data.copy()

        data.pop('username')

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'required'
        )

    def test_create_user_password_not_sent(self):
        '''Create a new User - Invalid :- When the password not passed'''
        data = self.valid_data.copy()

        data.pop('password')

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'required'
        )

    def test_create_user_multiple_fields_not_sent(self):
        '''Create a new User - Invalid :-
        When the password, email and firstname are not passed'''
        data = self.valid_data.copy()

        data.pop('email')

        data.pop('password')
        data.pop('first_name')

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'required'
        )
        self.assertEqual(
            response.data.get('errors').get('first_name')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('first_name')['type'],
            'required'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['message'],
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['type'],
            'required'
        )

    def test_create_user_email_already_exists(self):
        '''Create a new User - Invalid :-
        When the email has already been used before
        '''
        data = self.valid_data.copy()

        data['email'] = self.initial_user.email

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('email')['message'],
            'This field must be unique.'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['type'],
            'unique'
        )

    def test_create_user_username_already_exists(self):
        '''Create a new User - Invalid :-
        When the username has already been used before
        '''
        data = self.valid_data.copy()

        data['username'] = self.initial_user.username

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'This field must be unique.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'unique'
        )

    def test_create_user_email_username_already_exists(self):
        '''Create a new User - Invalid :-
        When the username and email have already been used before
        '''
        data = self.valid_data.copy()

        data['username'] = self.initial_user.username
        data['email'] = self.initial_user.email

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'This field must be unique.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'unique'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['message'],
            'This field must be unique.'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['type'],
            'unique'
        )

    def test_create_user_password_too_short(self):
        '''Create a new User - Invalid :-
        When the does not match policy - Password too short
        '''
        data = self.valid_data.copy()

        data['password'] = 'short'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'Ensure this field has at least 8 characters.'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'min_length'
        )

    def test_create_user_password_no_uppercase(self):
        '''Create a new User - Invalid :- When the does not match policy -
        Password does not contain uppercase character
        '''
        data = self.valid_data.copy()

        data['password'] = 'no_uppercasepassw0rd'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'invalid'
        )

    def test_create_user_password_no_lowercase(self):
        '''Create a new User - Invalid :- When the does not match policy -
        Password does not contain lowercase character
        '''
        data = self.valid_data.copy()

        data['password'] = 'NO_LOWERCASEPASSW0RD'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'invalid'
        )

    def test_create_user_password_no_number(self):
        '''Create a new User - Invalid :- When the does not match policy -
        Password does not contain number
        '''
        data = self.valid_data.copy()

        data['password'] = 'NO_NUMBERinPassword'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'invalid'
        )

    def test_create_user_password_no_special_character(self):
        '''Create a new User - Invalid :- When the password does not match policy -
        Password does not contain special character
        '''
        data = self.valid_data.copy()

        data['password'] = 'noSpecialCharact3rs'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('password')['message'],
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )
        self.assertEqual(
            response.data.get('errors').get('password')['type'],
            'invalid'
        )

    def test_create_user_email_invalid_type(self):
        '''Create a new User - Invalid :- When the email is not of valid type
        '''
        data = self.valid_data.copy()

        data['email'] = 'testuser'

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('email')['message'],
            'Enter a valid email address.'
        )
        self.assertEqual(
            response.data.get('errors').get('email')['type'],
            'invalid'
        )
        self.assertEqual(response.data.get('message'), 'An error has occured.')

    def test_create_user_username_invalid_type(self):
        '''Create a new User - Invalid :- When the username is not of valid type
        '''
        data = self.valid_data.copy()

        data['username'] = 'test user@12'  # username has space, and @

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertFalse(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('errors').get('username')['message'],
            'Username can only contain alphanumeric characters and . or _.'
        )
        self.assertEqual(
            response.data.get('errors').get('username')['type'],
            'invalid'
        )
        self.assertEqual(response.data.get('message'), 'An error has occured.')


class AccountsTestValid(AccountsTest):
    '''Create a new User - VALID :- When data valid'''

    def test_create_user_valid_data(self):
        data = self.valid_data.copy()

        response = self.client.post(
            reverse('accounts-create-user', kwargs={"version": "v1"}),
            data
        )

        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('message'),
            'User Account Created Successfully.'
        )
        self.assertNotContains(
            response, 'errors', status_code=status.HTTP_201_CREATED)

        self.assertNotContains(response, 'password',
                               status_code=status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('payload')['username'],
            data['username']
        )
        self.assertEqual(response.data.get('payload')['email'], data['email'])
