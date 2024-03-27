from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel


class UserReference(AddonsServiceBaseModel):
    user_uri = models.URLField(unique=True, db_index=True, null=False)

    class Meta:
        verbose_name = "User Reference"
        verbose_name_plural = "User References"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "user-references"

    @property
    def owner_uri(self) -> str:
        return self.user_uri
