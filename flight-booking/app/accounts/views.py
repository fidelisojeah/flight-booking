from datetime import datetime

from rest_framework.viewsets import ViewSet
from rest_framework import (
    status,
    decorators
)

from . import (
    services as accounts_services
)
from app.helpers.response import Response
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.settings import api_settings


class UserAuthViewSet(ViewSet):
    '''
    Handles User Creation, Authentication
    '''
    @decorators.action(detail=False, methods=['post'])
    def auth_user(self, request, **kwargs):
        '''
        To authenticate a user -
        returns the users details with a token used
        Also creates a cookie with the token
        '''
        cookie_expiration = datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA

        authenticated_user, token = accounts_services.authenticate_user(
            request,
            data=request.data
        )

        response = Response(
            authenticated_user,
            message='Sign in Successful.',
        )
        response.set_cookie(
            api_settings.JWT_AUTH_COOKIE,
            token,
            expires=cookie_expiration,
            httponly=True
        )
        return response

    @decorators.action(detail=False, methods=['post'])
    def create_user(self, request, **kwargs):
        '''To create a new user'''
        return Response(
            accounts_services.create_new_user(data=request.data),
            status=status.HTTP_201_CREATED,
            message='User Account Created Successfully.'
        )

    @decorators.action(detail=True, methods=['put', 'delete'], url_path='picture')
    def handle_profile_picture(self, request, **kwargs):
        '''To Update/Delete Profile Picture'''
        if request.method == 'PUT':
            return Response(
                accounts_services.update_profile_picture(
                    request.user,
                    account_id=kwargs.get('pk'),
                    data=request.FILES),
                status=status.HTTP_200_OK,
                message='Profile Picture Updated Successfully.'
            )
