from celery import Celery
from kombu import (
    Exchange,
    Queue,
)

from app import settings


deactivated_user_route = Queue(
    settings.EXCHANGE_NAME,
    Exchange(settings.EXCHANGE_NAME),
    routing_key=settings.DEACTIVATED_ROUTING_KEY,
)
reactivated_user_route = Queue(
    settings.EXCHANGE_NAME,
    Exchange(settings.EXCHANGE_NAME),
    routing_key=settings.REACTIVATED_ROUTING_KEY,
)
merged_user_route = Queue(
    settings.EXCHANGE_NAME,
    Exchange(settings.EXCHANGE_NAME),
    routing_key=settings.MERGED_ROUTING_KEY,
)

account_status_change_queues = [
    deactivated_user_route,
    reactivated_user_route,
    merged_user_route,
]

# Assuming 'app' is your Celery app instance
app = Celery()
app.conf.update(
    broker_url=settings.OSF_BROKER_URL,
    task_default_exchange=settings.EXCHANGE_NAME,
    task_default_exchange_type="direct",
    task_queues=(
        deactivated_user_route,
        reactivated_user_route,
        merged_user_route,
    ),
)
