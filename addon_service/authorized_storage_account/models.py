from django.contrib.postgres.fields import ArrayField
from django.db import models

from addon_service.utils.base_model import AddonsServiceBaseModel


class AuthorizedStorageAccount(AddonsServiceBaseModel):

    scopes = ArrayField(models.CharField(max_length=128), default=list, blank=True)
    default_root_folder = models.CharField()

    external_account = models.ForeignKey('addon_service.ExternalAccount', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Authorized Storage Account"
        verbose_name_plural = "Authorized Storage Accounts"
        app_label = "addon_service"
