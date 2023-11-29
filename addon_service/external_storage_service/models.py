from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel


class ExternalStorageService(AddonsServiceBaseModel):
    max_concurrent_downloads = models.IntegerField(null=False)
    max_upload_mb = models.IntegerField(null=False)

    auth_uri = models.URLField(null=False)

    external_service = models.ForeignKey(
        "addon_service.ExternalService", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "External Storage Service"
        verbose_name_plural = "External Storage Services"
        app_label = "addon_service"
