from datetime import timedelta
from rest_framework import (
    serializers,
    validators,
)
from app.accounts import serializer as accounts_serializers
from . import models as reservation_models


class AirlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = reservation_models.Airline
        fields = ('__all__')


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = reservation_models.Airport
        fields = ('__all__')


class FlightSchedulerSerializer(serializers.Serializer):
    period = serializers.IntegerField(required=True)
    time_of_flight = serializers.TimeField(required=True)
    flight_number = serializers.CharField(required=True, max_length=4)

    flight_duration = serializers.DurationField(
        max_value=timedelta(hours=24),
        required=True
    )
    departure_airport = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=reservation_models.Airport.objects.all()
    )
    arrival_airport = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=reservation_models.Airport.objects.all()
    )

    def validate_arrival_airport(self, arrival_airport):
        if self.initial_data.get('departure_airport', None) == arrival_airport.code:
            raise serializers.ValidationError(
                'Arrival airport cant be same as departure.')
        return arrival_airport

    def validate_departure_airport(self, departure_airport):
        if self.initial_data.get('arrival_airport', None) == departure_airport.code:
            raise serializers.ValidationError(
                'Arrival airport cant be same as departure.')
        return departure_airport


class FlightSerializer(serializers.ModelSerializer):
    flight_duration = serializers.CharField(
        source='get_flight_duration',
        read_only=True
    )
    flight_designation = serializers.CharField(
        source='get_flight_designation',
        read_only=True
    )
    departure_airport_view = AirportSerializer(
        source='departure_airport',
        read_only=True
    )
    arrival_airport_view = AirportSerializer(
        source='arrival_airport',
        read_only=True
    )
    airline_view = AirlineSerializer(
        source='airline',
        read_only=True
    )
    flight_number = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = reservation_models.Flight
        exclude = ('created_at', 'updated_at')

    def validate_arrival_airport(self, arrival_airport):
        if self.initial_data.get('departure_airport', None) == arrival_airport.code:
            raise serializers.ValidationError(
                'Arrival airport cant be same as departure.')
        return arrival_airport

    def validate_departure_airport(self, departure_airport):
        if self.initial_data.get('arrival_airport', None) == departure_airport.code:
            raise serializers.ValidationError(
                'Arrival airport cant be same as departure.')
        return departure_airport


class ReservationSerializer(serializers.ModelSerializer):
    first_flight_view = FlightSerializer(read_only=True, source='first_flight')
    return_view = FlightSerializer(read_only=True, source='return_flight')

    reserved_by = accounts_serializers.CompactAccountsViewSerializer(
        source='author',
        read_only=True
    )

    reservation_type = serializers.CharField(
        read_only=True,
        source='get_ticket_type_display'
    )
    reservation_class = serializers.CharField(
        read_only=True,
        source='get_flight_class_display'
    )

    class Meta:
        model = reservation_models.Reservation
        exclude = ('created_at', 'updated_at', 'deleted_at')


class AirlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = reservation_models.Airline
        fields = ('__all__')
