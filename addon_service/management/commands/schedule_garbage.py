import random
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from addon_service.tasks.key_rotation import schedule_encryption_rotation__celery
from app import celery_app


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise RuntimeError("scheduling garbage is only for debugging")
        while True:
            self.stdout.write("scheduling...")
            _schedule_backchannel_msg()
            schedule_encryption_rotation__celery.apply_async()
            time.sleep(10)


def _schedule_backchannel_msg():
    with celery_app.producer_pool.acquire() as producer:
        producer.publish(
            body={
                "action": (
                    "reactivate" if random.choice((True, False)) else "deactivate"
                ),
                "user_uri": "http://osf.example/user",
            },
            exchange="",
            routing_key=settings.OSF_BACKCHANNEL_QUEUE_NAME,
            serializer="json",
        )
