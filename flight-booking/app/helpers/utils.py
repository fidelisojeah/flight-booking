from rest_framework import (
    status,
    exceptions,
    serializers
)
from rest_framework_jwt.settings import api_settings
from app.accounts.serializer import(
    UserSerializer
)
from django.conf import settings


class FieldErrorExceptions(exceptions.APIException):
    '''
    Custom Exception of missing fields
    '''
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid'
    default_detail = 'Fields Missing.'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = detail
        self.code = code


def validate_fields_present(data, *args, **kwargs):
    '''
    Validate fields are present in `data`
    _Usage_: `validate_fields_present(data, 'field1', 'field2', ...)`
    '''
    errors = {}
    fields = {}

    for count, key in enumerate(args):
        if (data.get(key, None) or None) is None:
            errors[key] = {
                'message': 'This field can not be left blank.',
                'type': 'required'
            }
        else:
            fields[key] = data.get(key, None)

    if kwargs.get('raise_exception', False) and errors:
        raise FieldErrorExceptions(errors)

    return fields


def jwt_response_payload_handler(token, user=None, request=None):
    '''custom jwt response payload including user details'''
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


def generate_token(user):
    token = api_settings.JWT_ENCODE_HANDLER(
        api_settings.JWT_PAYLOAD_HANDLER(user)
    )

    return '{} {}'.format(settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX'], token)

