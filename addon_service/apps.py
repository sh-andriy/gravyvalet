import threading

from django.apps import AppConfig

from addon_service.tasks import listen_for_osf_signals


class AddonServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "addon_service"

    def ready(self):
        thread = threading.Thread(target=listen_for_osf_signals)
        thread.daemon = True
        thread.start()
