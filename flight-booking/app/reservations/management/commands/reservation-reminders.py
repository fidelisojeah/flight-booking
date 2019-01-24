from django.utils import timezone

from django.db import models
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import send_mail

from app.reservations.models import Reservation
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        # a = send_mail('Test Mail from Me', 'This is just a test email from Fidelis',
        #           'no_reply@anvar.tech', ['fidelis.ojeah@gmail.com'])
        today = timezone.now().replace(hour=0, minute=0, second=0)
        end_day = today.replace(hour=23, minute=59, second=59)

        today_reservations = Reservation.objects.filter(
            models.Q(
                first_flight__expected_departure__range=[today, end_day]
            ) |
            models.Q(
                return_flight__expected_departure__range=[today, end_day]
            )
        )
        reservation = today_reservations[0]
        flight = reservation.first_flight
        if reservation.first_flight.expected_departure < today:
            flight = today_reservations.return_flight

        reservation_url = 'reservations/{}/'.format(reservation.id)
        site = settings.APP_URL

        html = render_to_string('flight_reservation.html', {
            'flight': flight,
            'reservation': reservation,
            'reservation_url': reservation_url,
            'email_information': 'Your Flight is Coming Up Soon',
            'site': site,
            'email_title': 'Reservation For {}'.format(reservation.author.get_full_name())
        })
        print(html)
