from django.db import models

from addon_service.utils.base_model import AddonsServiceBaseModel


class StorageServiceSettings(AddonsServiceBaseModel):

    max_concurrent_downloads = models.IntegerField(null=False)
    max_upload_mb = models.IntegerField(null=False)

    auth_uri = models.URLField(null=False)

    external_service = models.ForeignKey('addon_service.ExternalService', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Storage Service Settings"
        verbose_name_plural = "Storage Service Settings"
        app_label = "addon_service"
