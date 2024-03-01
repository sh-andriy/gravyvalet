import logging
from celery import Celery
from kombu import Consumer, Exchange, Queue

from addon_service.models import UserReference
from app.settings import OSF_BROKER_URL

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OSF_DEFAULT_QUEUE = "celery"


def process_disabled_user_message(body, message):
    user_uri = body.get("user_uri")
    try:
        UserReference.objects.get(user_uri=user_uri).delete()
        message.ack()
        logger.info(f"Processed and disabled user: {user_uri}")
    except Exception as e:
        # TODO: Sentry?
        logger.exception(f"Error when processing user: {user_uri}. Error: {e}")
        message.reject()


def listen_for_osf_signals():
    logger.info("Starting to listen for OSF signals...")
    try:
        with Celery(broker=OSF_BROKER_URL).connection() as connection:
            with Consumer(
                connection,
                queues=Queue(
                    name=OSF_DEFAULT_QUEUE,
                    exchange=Exchange(OSF_DEFAULT_QUEUE),
                ),
                callbacks=[process_disabled_user_message],
                accept=["json"],
            ):
                logger.info("Consumer set up successfully. Waiting for messages...")
                while True:
                    connection.drain_events()
    except Exception as e:
        logger.exception(f"An error occurred while listening for signals: {e}")

