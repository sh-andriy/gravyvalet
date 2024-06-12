import datetime

import celery

from addon_service.credentials.models import ExternalCredentials


def schedule_encryption_rotation(earlier_than: datetime.datetime | None = None):
    _pks = ExternalCredentials.objects.filter(
        modified__lte=(earlier_than or datetime.datetime.now(tz=datetime.UTC))
    ).values_list("pk", flat=True)
    for _credentials_pk in _pks.iterator():
        rotate_credentials_encryption__celery.apply_async([_credentials_pk])


@celery.shared_task(acks_late=True)
def schedule_encryption_rotation__celery(earlier_than: str = ""):
    schedule_encryption_rotation(
        datetime.datetime.fromisoformat(earlier_than) if earlier_than else None
    )


@celery.shared_task(acks_late=True)
def rotate_credentials_encryption__celery(credentials_pk: str):
    ExternalCredentials.objects.get(pk=credentials_pk).rotate_encryption()
