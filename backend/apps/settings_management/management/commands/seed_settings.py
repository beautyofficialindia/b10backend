# Seed command will be implemented in Task Group 5
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed default settings'

    def handle(self, *args, **options):
        self.stdout.write('seed_settings: not yet implemented')
