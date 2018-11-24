from rest_framework import (
    views,
    exceptions
)
from . import utils


def handle_exceptions(exc, context):
    '''
    Custom exception handler for Django Rest Framework that adds
    the `status_code` to the response and adds a message
    that an error has occured and spreads validation errors.
    '''
    response = views.exception_handler(exc, context)

    if isinstance(exc, utils.FieldErrorExceptions):
        errors = exc.detail
    else:

        if hasattr(exc, 'detail'):
            errors = {
                'global': str(exc.detail)
            }
        else:
            errors = {
                'global': str(exc)
            }

    if isinstance(exc, exceptions.ValidationError):
        errors.pop('global', None)
        for key, value in exc.detail.items():
            if isinstance(value, list):
                errors[key] = {
                    'message': str(value[0]),
                    'type': value[0].code
                }
            else:
                errors[key] = {
                    'message': str(value),
                    'type': value.code
                }

    if response is not None:
        response.data = {}
        response.data['status_code'] = response.status_code
        response.data['errors'] = {
            **errors
        }
        response.data['message'] = 'An error has occured.'
        response.data['success'] = False

    return response
