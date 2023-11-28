from django.db import models

from addon_service.utils.base_model import AddonsServiceBaseModel


class ConfiguredStorageAddon(AddonsServiceBaseModel):

    root_folder = models.CharField()

    external_account = models.ForeignKey('addon_service.ExternalAccount', on_delete=models.CASCADE)
    internal_resource = models.ForeignKey('addon_service.InternalResource', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Configured Storage Addon"
        verbose_name_plural = "Configured Storage Addons"
        app_label = "addon_service"
