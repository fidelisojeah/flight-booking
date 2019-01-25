from rest_framework import (
    views,
    exceptions,
    status,
    response as api_response
)
import bugsnag
from cloudinary import api as cloudinary_api
from django.conf import settings

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
            if isinstance(value, dict):
                errors[key] = {
                }
                for _key, _value in value.items():
                    if isinstance(_value, list):

                        errors[key][_key] = {
                            'message': str(_value[0]),
                            'type': _value[0].code
                        }

            elif isinstance(value, list):
                errors[key] = {
                    'message': str(value[0]),
                    'type': value[0].code
                }
            else:
                errors[key] = {
                    'message': str(value),
                    'type': value.code
                }

    if isinstance(exc, cloudinary_api.Error):
        response = api_response.Response(
            data={'detail': 'cloudinary Error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        errors = {
            'global': 'An issue has occured with our cloudinary service.'
        }
    if response.status_code = status.is_server_error:
        bugsnag.notify(exc,
                       context=context,
                       )
    if response is not None:
        response.data = {}
        response.data['status_code'] = response.status_code
        response.data['errors'] = {
            **errors
        }
        response.data['message'] = 'An error has occured.'
        response.data['success'] = False

    return response
