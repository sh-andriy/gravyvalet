import logging

import celery

from addon_service.models import UserReference


logger = logging.getLogger(__name__)


def get_handler_signature(message_body_json: dict):
    # handle custom "account status update" messages from osf:
    # https://github.com/CenterForOpenScience/osf.io/blob/develop/osf/external/messages/celery_publishers.py
    _action = message_body_json.get("action")
    match _action:
        case "deactivate":
            _signature = user_deactivated.s(user_uri=message_body_json["user_uri"])
        case "reactivate":
            _signature = user_reactivated.s(user_uri=message_body_json["user_uri"])
        case "merge":
            _signature = users_merged.s(
                into_user_uri=message_body_json["into_user_uri"],
                from_user_uri=message_body_json["from_user_uri"],
            )
        case _:
            raise NotImplementedError(f"Action {_action} is not Implemented")
    logger.info(
        'osf-backchannel "%s" message received and enqueued for handling', _action
    )
    return _signature


@celery.shared_task(acks_late=True)
def user_deactivated(user_uri: str):
    try:
        UserReference.objects.get(user_uri=user_uri).deactivate()
    except UserReference.DoesNotExist:
        pass


@celery.shared_task(acks_late=True)
def user_reactivated(user_uri: str):
    try:
        UserReference.objects.get(user_uri=user_uri).reactivate()
    except UserReference.DoesNotExist:
        pass


@celery.shared_task(acks_late=True)
def users_merged(into_user_uri: str, from_user_uri: str):
    try:
        _from_user = UserReference.objects.get(user_uri=from_user_uri)
    except UserReference.DoesNotExist:
        pass  # nothing to do without a "from" user
    else:
        _into_user = UserReference.objects.get_or_create(user_uri=into_user_uri)
        _into_user.merge(_from_user)
