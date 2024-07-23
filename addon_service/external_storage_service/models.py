from django.db import models

from addon_service.abstract.external_storage.models import ExternalService
from addon_service.common.validators import validate_storage_imp_number


class ExternalStorageService(ExternalService):
    int_addon_imp = models.IntegerField(
        null=False,
        validators=[validate_storage_imp_number],
        verbose_name="Addon implementation",
    )
    max_concurrent_downloads = models.IntegerField(null=False)
    max_upload_mb = models.IntegerField(null=False)
    wb_key = models.CharField(null=False, blank=True, default="")

    class Meta:
        verbose_name = "External Storage Service"
        verbose_name_plural = "External Storage Services"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "external-storage-services"
