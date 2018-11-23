from django.db import (
    transaction
)

from . import serializer as account_serializer


def create_new_user(*, data):
    '''Creates a new user'''
    serializer = account_serializer.UserAuthSerializer(
        data=data
    )
    with transaction.atomic():
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    return serializer.data
