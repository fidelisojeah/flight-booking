from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission, Group, User
from django.apps import apps
from django.core.management import BaseCommand

from app.accounts.models import Accounts
from app.accounts.permissions import GROUPS


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('fixing user permissions')
        # delete pre-existing user permission

        Group.objects.all().delete()
        Permission.objects.all().delete()

        print('Creating permissions')
        for app_config in apps.get_app_configs():
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=3)
            app_config.models_module = None

        print('Creating groups and assigning permissions')
        for group, group_permissions in GROUPS.items():
            new_group, created = Group.objects.get_or_create(name=group)

            for each_model, each_permission in group_permissions:
                try:
                    permission = Permission.objects.get(
                        codename=each_permission,
                    )

                    new_group.permissions.add(
                        permission
                    )
                    print('Adding Permission {}.{} to Group {} | {}'.format(
                        permission.content_type.name,
                        permission.codename,
                        new_group,
                        permission.name
                    ))
                except Exception as exc:
                    print('Error Occured: ', exc)
                    pass
            if group == 'client':
                for user in User.objects.filter(
                    account__user_type=Accounts.CLIENT
                ):
                    user.groups.add(new_group)
                    print('Adding User {} to Group {} '.format(
                        user.first_name,
                        group,
                    ))
            if group == 'staff':
                for user in User.objects.filter(
                    account__user_type=Accounts.STAFF
                ):
                    user.groups.add(new_group)
                    print('Adding User {} to Group {} '.format(
                        user.first_name,
                        group,
                    ))
            if group == 'super_staff':
                for user in User.objects.filter(
                    account__user_type=Accounts.SUPER_STAFF
                ):
                    user.groups.add(new_group)
                    print('Adding User {} to Group {} '.format(
                        user.first_name,
                        group,
                    ))
