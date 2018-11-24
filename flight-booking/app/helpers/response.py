from rest_framework import (
    status as drf_status,
    response as drf_response
)
from app.accounts.serializer import(
    UserSerializer
)


class Response(drf_response.Response):
    '''Custom API response -
    Data would be appended to it
    '''

    def __init__(self, old_data=None, **kwargs):

        status = kwargs.get('status', drf_status.HTTP_200_OK)

        data = {
            'status_code': status,
            'payload': old_data,
            'message': 'Returned Successfully.',
            'success': True
        }

        if status == drf_status.HTTP_201_CREATED:
            data['message'] = 'Created Successfully.'

        custom_message = kwargs.pop('message', None)

        if custom_message is not None:
            data['message'] = custom_message

        super(Response, self).__init__(
            data, **kwargs
        )
