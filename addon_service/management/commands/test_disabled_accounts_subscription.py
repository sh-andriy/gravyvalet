from django.core.management.base import BaseCommand

from addon_service.listeners import listen_for_disabled_users


class Command(BaseCommand):
    help = "Subscribes to an RPC exchange and listens for messages."

    def handle(self, *args, **options):
        listen_for_disabled_users()
