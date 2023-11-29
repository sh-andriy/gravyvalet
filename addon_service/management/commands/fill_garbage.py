from django.conf import settings
from django.core.management.base import LabelCommand

from addon_service import models as db


class Command(LabelCommand):
    """add garbage to the database for local/manual testing

    provide one or more labels; will create one set of connected objects for each label
    """

    def handle_label(self, label, **options):
        if not settings.DEBUG:
            raise Exception("must have DEBUG set to eat garbage")
        _es = db.ExternalService.objects.create(name=f"entity-{label}")
        _ess = db.ExternalStorageService.objects.create(
            max_concurrent_downloads=2,
            max_upload_mb=2,
            auth_uri=f"http://foo.example/{label}",
            external_service=_es,
        )
        for _i in range(3):
            _iu = db.InternalUser.objects.create(
                user_uri=f"http://osf.example/u{label}",
            )
            _ec = db.ExternalCredentials.objects.create()
            _ea = db.ExternalAccount.objects.create(
                remote_account_id=label,
                remote_account_display_name=label,
                external_service=_es,
                owner=_iu,
                credentials=_ec,
            )
            _asa = db.AuthorizedStorageAccount.objects.create(
                external_storage_service=_ess,
                external_account=_ea,
            )
            for _i in range(5):
                _ir = db.InternalResource.objects.create(
                    resource_uri=f"http://osf.example/r{label}",
                )
                _csa = db.ConfiguredStorageAddon.objects.create(
                    authorized_storage_account=_asa,
                    internal_resource=_ir,
                )
        return str(_csa)
