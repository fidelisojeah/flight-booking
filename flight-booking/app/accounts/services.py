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
    exceptions,
    generics
)
from app.helpers import (
    utils
)

from .models import Accounts
from . import serializer as account_serializer
from app.uploads import services as upload_services


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


def update_profile_picture(requestor, *, account_id, data):
    '''Upload/Edit Profile Picture'''
    # if requestor.has_perm('accounts.update_any_picture'):
    #     pass
    # elif requestor.has_perm('accounts.update_own_picture'):
    #     if requestor.accounts.id != account_id:
    #         raise exceptions.PermissionDenied('Insufficient Permission.')
    #     account_id = requestor.accounts.id
    # else:
    #     raise exceptions.PermissionDenied('Insufficient Permission.')

    image_serializer = account_serializer.ImageUploadSerializer(
        data=data
    )

    image_serializer.is_valid(raise_exception=True)

    user_account = generics.get_object_or_404(Accounts, pk=account_id)

    profile_picture_public_id = 'profiles/{}'.format(
        user_account.id)
    # UPLOAD profile Picture

    image_upload = upload_services.upload_picture(
        image_serializer.validated_data.get('profile_picture'),
        picture_public_id=profile_picture_public_id
    )

    user_account.profile_picture_public_id = profile_picture_public_id
    user_account.profile_picture_url = image_upload.get('secure_url')

    user_account.save()

    return account_serializer.UserSerializer(user_account.user).data
