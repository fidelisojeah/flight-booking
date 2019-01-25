from django.http import HttpResponse
from django.template import loader
from django.conf import settings


def index(request):
    '''Load index file'''
    template = loader.get_template('index.html')
    context = {
        'site_url': settings.APP_URL
    }
    return HttpResponse(template.render(context, request))
