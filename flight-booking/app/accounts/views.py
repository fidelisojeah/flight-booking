from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    decorators
)

from . import serializer


# Create your views here.
class UserAuthViewSet(ViewSet):
    '''
    Handles User Creation, Authentication
    '''
    @decorators.action(detail=False, methods=['post'])
    def create_user(self, request, **kwargs):
        pass
