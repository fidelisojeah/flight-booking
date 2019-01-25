from django.utils import timezone

from django.db import models
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from app.reservations.models import Reservation
from django.conf import settings

from app.helpers import mails


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
        ).exclude(is_reminder_sent=True)

        if not today_reservations.exists():
            return 'Done! No Upcoming Reservations.'

        for reservation in today_reservations:
            flight = reservation.first_flight
            if reservation.first_flight.expected_departure < today and today_reservations.return_flight:
                flight = today_reservations.return_flight

            reservation_url = '/api/v1/reservations/{}/'.format(reservation.id)
            site = settings.APP_URL

            email_title = 'Flight Reservation For {}'.format(
                reservation.author.get_full_name())

            email_data = {
                'flight': flight,
                'reservation': reservation,
                'reservation_url': reservation_url,
                'email_information': 'Your Flight is Coming Up Soon',
                'site': site,
                'email_title': email_title
            }

            email_html = render_to_string(
                'flight_reservation.html', email_data)
            email_text = render_to_string('flight_reservation.txt', email_data)

            mail_sent = mails.send_email(
                subject=email_title,
                email_from='Flight Booking Reservations <reservartions@{}>'.format(
                    settings.EMAIL_DOMAIN_URL),
                email_to=reservation.author.user.email,
                email_message=email_html,
                email_message_txt=email_text
            )

            reservation.is_reminder_sent = True
            reservation.save()

        return 'Done! All Reminder Emails sent.'
