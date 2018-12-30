from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.apps import apps
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('fixing user permissions')
        # delete pre-existing user permission
        Permission.objects.all().delete()

        for app_config in apps.get_app_configs():
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=3)
            app_config.models_module = None
