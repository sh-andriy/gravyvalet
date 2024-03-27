from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel
from addon_service.common.credentials import CredentialsFormats
from addon_service.common.enums.validators import validate_credentials_format


class CredentialsIssuer(AddonsServiceBaseModel):
    name = models.CharField(null=False)
    int_credentials_format = models.IntField(
        null=False,
        validators=[validate_credentials_format],
    )
    auth_uri = models.URLField(null=False)

    class Meta:
        verbose_name = "External Service"
        verbose_name_plural = "External Services"
        app_label = "addon_service"

    @property
    def credentials_format(self):
        return CredentialsFormats(self.int_credentials_format)
