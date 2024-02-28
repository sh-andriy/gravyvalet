import Celery

from kombu import Queue, Exchange, Consumer
OSF_DEFAULT_QUEUE = 'celery'
from addon_service.models import UserReference
from app.settings import OSF_BROKER_URL

def process_disabled_user_message(body, message):
    print(f"Received message: {body}")
    user_uri = body['user_uri']
    UserReference.objects.get(user_uri=user_uri).delete()
    message.ack()


def listen_for_osf_signals():
    with Celery(broker=OSF_BROKER_URL).connection() as connection:
        with Consumer(
                connection,
                queues=Queue(
                    name=OSF_DEFAULT_QUEUE,  # TODO: Any plans here?
                    exchange=Exchange(OSF_DEFAULT_QUEUE),  # TODO: Define exchange(s) for merged/disabled
                ),
                callbacks=[  # TODO: Multiple callbacks or multiple queues?
                    process_disabled_user_message
                ],
                accept=['json']
        ):
            while True:
                connection.drain_events()