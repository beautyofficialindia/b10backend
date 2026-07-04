import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Creates default admin account and groups'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        sales_group, _ = Group.objects.get_or_create(name='Sales')
        support_group, _ = Group.objects.get_or_create(name='Support')

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@b10itsolution.com')
        password = os.environ.get('ADMIN_PASSWORD', 'admin')

        # Create admin user
        if not User.objects.filter(username=username).exists():
            admin = User.objects.create_superuser(username, email, password)
            admin.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {username}'))
