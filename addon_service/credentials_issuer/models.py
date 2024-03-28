from django.core.exceptions import ValidationError
from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel
from addon_service.common.credentials import CredentialsFormats
from addon_service.common.enums.validators import validate_credentials_format


class CredentialsIssuer(AddonsServiceBaseModel):
    name = models.CharField(null=False)
    int_credentials_format = models.IntegerField(
        null=False,
        validators=[validate_credentials_format],
    )
    auth_uri = models.URLField(null=False)
    oauth_client_id = models.CharField(null=True)

    class Meta:
        verbose_name = "External Service"
        verbose_name_plural = "External Services"
        app_label = "addon_service"

    @property
    def credentials_format(self):
        return CredentialsFormats(self.int_credentials_format)

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.credentials_format is CredentialsFormats.OAUTH2 and not self.oauth_client_id:
            raise ValidationError("OAuth2 Apps must register their client ID")
