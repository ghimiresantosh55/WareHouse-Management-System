from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        call_command("migrate_schemas")
        call_command("migrate_history_schemas", "--database=log_db")
  
