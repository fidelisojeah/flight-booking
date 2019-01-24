from rest_framework.viewsets import ViewSet

from rest_framework import (
    status,
    decorators
)

from app.helpers.response import Response
from app.helpers.pagination import paginate
from app.reservations import (
    services as reservation_services,
    serializers as reservation_serializers
)


class ReservationViewSet(ViewSet):
    '''
    list:
    List/Filter Reservations extra queries: flight_number, date

    retrieve:
    Retrieve Single Reservation

    create:
    Create Single Reservation (Book Reservation)
    '''

    def list(self, request, **kwargs):
        '''
        get:
        List/Filter Reservations extra queries: flight_number, date
        '''
        reservations = reservation_services.filter_reservations(
            request.user,
            request.query_params
        )
        return Response(
            paginate(
                serializer=reservation_serializers.ReservationSerializer,
                query_set=reservations, request=request
            )
        )

    def retrieve(self, request, **kwargs):
        '''
        get:
        Retrieve Single Reservation
        '''
        return Response(
            reservation_services.retrieve_reservation(
                request.user,
                reservation_pk=kwargs.get('pk'),
                query_params=request.query_params
            )
        )

    def create(self, request, **kwargs):
        '''
        post:
        Create Single Reservation (Book Reservation)
        '''
        return Response(
            reservation_services.make_own_reservation(
                request.user,
                data=request.data
            ),
            status=status.HTTP_201_CREATED
        )

    @decorators.action(detail=True, methods=['get'], url_path='email')
    def send_reservation_email(self, request, **kwargs):
        return Response(
            reservation_services.send_reservation_email(
                request.user,
                kwargs.get('pk')
            ),
            message='Email Sent!.'
        )

    @decorators.action(detail=False, methods=['get'], url_path='(?P<year>[1-2][0-9][0-9][0-9])')
    def filter_reservations_by_year(self, request, **kwargs):
        '''
        get:
        Filter Reservations by year
        '''
        reservations = reservation_services.filter_reservations_by_period(
            request.user,
            month=0,
            period='year',
            year=kwargs.get('year', 0),
            query_params=request.query_params
        )
        return Response(
            paginate(
                serializer=reservation_serializers.ReservationSerializer,
                query_set=reservations,
                request=request,
            )
        )

    @decorators.action(detail=False, methods=['get'], url_path='(?P<year>[1-2][0-9][0-9][0-9])/(?P<month>[0-9]+)')
    def filter_reservations_by_month(self, request, **kwargs):
        '''
        get:
        Filter Reservations by year and month extra queries: flight_number, date
        '''
        reservations = reservation_services.filter_reservations_by_period(
            request.user,
            month=kwargs.get('month', 0),
            period='month',
            year=kwargs.get('year', 0),
            query_params=request.query_params
        )

        return Response(
            paginate(
                serializer=reservation_serializers.ReservationSerializer,
                query_set=reservations,
                request=request,
            )
        )


class AccountReservationViewSet(ViewSet):
    @decorators.action(detail=True, methods=['post', 'get'], url_path='reservations')
    def reservations(self, request, **kwargs):
        '''
        get:
        View Reservations for account based on account id extra queries: flight_number, date

        post:
        Create Reservation For account based on account id
        '''
        if request.method == 'GET':
            reservations = reservation_services.filter_reservations(
                request.user,
                request.query_params,
                account_pk=kwargs.get('pk')
            )

            return Response(
                paginate(
                    serializer=reservation_serializers.ReservationSerializer,
                    query_set=reservations,
                    request=request
                )

            )
        if request.method == 'POST':
            return Response(
                reservation_services.make_reservation(
                    request.user,
                    account_pk=kwargs.get('pk'),
                    data=request.data
                ),
                status=status.HTTP_201_CREATED,
                message='Reservation made Successfully.'
            )


class FlightsViewSet(ViewSet):
    '''
    list:
    List/Filter Flights extra queries: from, destination, date

    retrieve:
    Retrieve Single Flight based on id

    create:
    Create Single Reservation (Book Reservation)
    '''

    def list(self, request, **kwargs):
        '''
        get:
        List/Filter Flights extra queries: from, destination, date
        '''
        return Response(
            reservation_services.filter_flights(
                request.user,
                query_params=request.query_params
            )
        )

    def retrieve(self, request, **kwargs):
        '''
        get:
        Retrieve Single Flight Information
        '''
        return Response(
            reservation_services.retrieve_flight(
                request.user,
                kwargs.get('pk')
            )
        )

    @decorators.action(detail=True, methods=['get', 'post'], url_path='reservations')
    def reservations(self, request, **kwargs):
        '''
        get:
        Retrieve Reservation information for flight

        post:
        Make reservation for flight
        '''
        if request.method == 'GET':
            return Response(
                reservation_services.filter_flight_reservations(
                    request.user,
                    kwargs.get('pk')
                )
            )
        if request.method == 'POST':
            return Response(
                reservation_services.make_flight_reservation(
                    request.user,
                    flight_pk=kwargs.get('pk'),
                    data=request.data
                )
            )


class AirlineViewSet(ViewSet):
    '''
    list:
    List/Filter Airlines
    '''

    def list(self, request, **kwargs):
        airlines = reservation_services.filter_airlines(
            request.user,
            request.query_params,
        )
        return Response(
            paginate(
                request=request,
                query_set=airlines,
                serializer=reservation_serializers.AirlineSerializer
            )
        )

    @decorators.action(detail=True, methods=['post', 'get'], url_path='schedule')
    def schedule(self, request, **kwargs):
        '''
        get:
        Retrieve Flight schedule for Airline

        post:
        Create Single airline flight schedule
        '''
        if request.method == 'GET':
            return Response(
                reservation_services.retrieve_flight_for_airline(
                    request.user,
                    airline_code=kwargs.get('pk'),
                    query_params=request.query_params
                ),
                message='Available Flights For Airline: {} Returned'.format(
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
        '''
        post:
        Schedule Regular daily flights for airline
        '''
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
        '''
        post:
        Schedule Regular weekly flights for airline
        '''
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
