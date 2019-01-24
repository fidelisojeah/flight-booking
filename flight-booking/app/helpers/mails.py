from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site


def send_email():
    site = Site.objects.first().domain
