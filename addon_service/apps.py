import threading

from django.apps import AppConfig


class AddonServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "addon_service"

    def ready(self):
        super().ready()
        from addon_service.listeners import listen_for_osf_signals
        thread = threading.Thread(target=listen_for_osf_signals)
        thread.daemon = True
        thread.start()
