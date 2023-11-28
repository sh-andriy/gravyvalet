from django.db import models

from addon_service.utils.base_model import AddonsServiceBaseModel


class ExternalService(AddonsServiceBaseModel):

    name = models.CharField(null=False)

    class Meta:
        verbose_name = "External Service"
        verbose_name_plural = "External Services"
        app_label = "addon_service"
