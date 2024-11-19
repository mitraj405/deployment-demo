# your_app/management/commands/startserver.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Start the server'

    def handle(self, *args, **options):
        port = os.environ.get("PORT", "8000")  # Default to 8000 if PORT is not set
        call_command('runserver', f'0.0.0.0:{port}')
