from django.db import models

from addon_service.utils.base_model import AddonsServiceBaseModel


class InternalResource(AddonsServiceBaseModel):
    resource_uri = models.URLField(unique=True, db_index=True, null=False)

    class Meta:
        verbose_name = "Internal Resource"
        verbose_name_plural = "Internal Resources"
        app_label = "addon_service"
