from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    decorators
)

from . import (
    services as accounts_services
)


# Create your views here.
class UserAuthViewSet(ViewSet):
    '''
    Handles User Creation, Authentication
    '''
    @decorators.action(detail=False, methods=['post'])
    def create_user(self, request, **kwargs):
        return Response(
            accounts_services.create_new_user(data=request.data),
            status=status.HTTP_201_CREATED
        )
