from rest_framework.viewsets import ViewSet

from app.helpers.response import Response
from rest_framework import (
    status,
    decorators
)

from app.reservations import services as reservation_services


class ReservationViewSet(ViewSet):
    # TODO: Allow user book reservation
    # tests
    # permissions
    def create(self, request, **kwargs):
        return Response(
            reservation_services.make_own_reservation(
                request.user,
                data=request.data
            )
        )

    @decorators.action(detail=True, methods=['post', 'get'], url_path='book')
    def book_reservation(self, request, **kwargs):
        return Response(
            reservation_services.make_reservation(
                request.user,
                account_pk=kwargs.get('pk'),
                data=request.data
            )
        )


class FlightsViewSet(ViewSet):

    def list(self, request, **kwargs):
        return Response(
            reservation_services.filter_flights(
                request.user,
                query_params=request.query_params
            )
        )

    def retrieve(self, request, **kwargs):
        return Response(
            reservation_services.retrieve_flight(
                request.user,
                kwargs.get('pk')
            )
        )

    @decorators.action(detail=True, methods=['post', 'get'], url_path='schedule')
    def schedule(self, request, **kwargs):
        if request.method == 'GET':
            return Response(
                reservation_services.retrieve_flight_for_airline(
                    request.user,
                    airline_code=kwargs.get('pk'),
                    query_params=request.query_params
                ),
                message='Available Flights For Airport: {} Returned'.format(
                    kwargs.get('pk'))
            )
        if request.method == 'POST':
            return Response(
                reservation_services.schedule_flight(
                    request.user,
                    airline_code=kwargs.get('pk'),
                    data=request.data
                ),
                message='Flight Scheduled Successfully',
                status=status.HTTP_201_CREATED
            )

    @decorators.action(detail=True, methods=['post'], url_path='daily-schedule')
    def daily_schedule(self, request, **kwargs):
        return Response(
            reservation_services.bulk_schedule_flight(
                request.user,
                period_type='days',
                airline_code=kwargs.get('pk'),
                data=request.data
            ),
            message='Flights Scheduled Successfully',
            status=status.HTTP_201_CREATED
        )

    @decorators.action(detail=True, methods=['post'], url_path='weekly-schedule')
    def weekly_schedule(self, request, **kwargs):
        return Response(
            reservation_services.bulk_schedule_flight(
                request.user,
                period_type='weeks',
                airline_code=kwargs.get('pk'),
                data=request.data
            ),
            status=status.HTTP_201_CREATED,
            message='Flights Scheduled Successfully',
        )
