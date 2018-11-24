from django.utils import timezone
from django.db import (
    transaction
)
from django.contrib.auth import (
    authenticate,
    user_logged_in,
    models as auth_models
)
from django.db.models import Q

from rest_framework_jwt.settings import api_settings
from rest_framework import (
    exceptions
)
from app.helpers import (
    utils
)
from . import serializer as account_serializer


def create_new_user(*, data):
    '''Creates a new user'''
    serializer = account_serializer.UserSerializer(
        data=data
    )
    with transaction.atomic():
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    return serializer.data


def authenticate_user(request, *, data):
    '''Authenticates the user'''
    valid_data = utils.validate_fields_present(
        data, 'username', 'password',
        raise_exception=True
    )
    user_model = auth_models.User.objects.filter(
        Q(username=valid_data.get('username')) |
        Q(email__iexact=valid_data.get('username'))
    ).first()

    if user_model is not None:
        credentials = {
            'username': user_model.username,
            'password': valid_data.get('password')
        }
        if all(credentials.values()):
            user = authenticate(request=request, **credentials)

            if user and user.is_active:
                payload = api_settings.JWT_PAYLOAD_HANDLER(user)
                token = api_settings.JWT_ENCODE_HANDLER(payload)

                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)

                return utils.jwt_response_payload_handler(
                    token,
                    user
                ), token

    raise exceptions.NotAuthenticated(
        'Unable to log in with provided credentials.'
    )
