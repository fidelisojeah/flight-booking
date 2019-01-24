from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

from django.conf import settings


def send_email(*,
               subject='Flight Booking: ',
               email_from='Flight bookings <no_reply@{}>'.format(settings.EMAIL_DOMAIN_URL),
               email_to,
               email_message_txt='',
               email_message
               ):
    '''Send Out Emails'''
    email = EmailMultiAlternatives(subject, email_message_txt, email_from)
    email.attach_alternative(email_message, 'text/html')
    email.to = [email_to]

    email.send()

    return email
