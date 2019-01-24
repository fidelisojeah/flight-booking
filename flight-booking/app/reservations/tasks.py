from celery import (shared_task, decorators)
from django.template.loader import render_to_string
from django.utils import timezone

from app.reservations.models import Reservation
from django.conf import settings

from app.helpers import mails


@decorators.task(name='send_reservation_information',
                 bind=True,
                 default_retry_delay=60 * 5,
                 retry_kwargs={'max_retries': 2})
def send_reservation_information(self, reservation_id):
    '''Send Reservation Information to User'''
    try:
        reservation = Reservation.objects.get(pk=reservation_id)
        flight = reservation.first_flight

        today = timezone.now()

        if reservation.first_flight.expected_departure < today and today_reservations.return_flight:
            flight = today_reservations.return_flight

        reservation_url = '/api/v1/reservations/{}/'.format(reservation.id)
        site = settings.APP_URL

        email_title = 'Your Flight Reservation for {}'.format(
            flight.get_flight_designation())

        email_data = {
            'flight': flight,
            'reservation': reservation,
            'reservation_url': reservation_url,
            'email_information': 'Your Flight Reservation Details',
            'site': site,
            'email_title': email_title
        }

        email_html = render_to_string(
            'flight_reservation.html', email_data)
        email_text = render_to_string('flight_reservation.txt', email_data)

        mails.send_email(
            subject=email_title,
            email_from='Flight Booking Reservations <reservartions@{}>'.format(
                settings.EMAIL_DOMAIN_URL),
            email_to=reservation.author.user.email,
            email_message=email_html,
            email_message_txt=email_text
        )
    except Reservation.DoesNotExist:
        pass
    except Exception as exc:
        self.retry(exc=exc)
