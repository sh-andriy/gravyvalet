from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel
from addon_service.common.credentials import CredentialsFormats
from addon_service.common.exceptions import InvalidCredentials


_CREDENTIALS_VALUE_FIELDS = [
    "user_name",
    "pwd",
    "service_host",
    "access_key",
    "secret_key",
    "oauth_access_token",
]


# TODO: Settle on encryption solution
class ExternalCredentials(AddonsServiceBaseModel):
    credentials_issuer = models.ForeignKey(
        "addons_service.CredentialsIssuer",
        on_delete=models.CASCADE,
        related_name="linked_credentials",
    )

    # For USER_PASS services (e.g. Boa)
    username = models.CharField(blank=True, null=True)
    pwd = models.CharField(blank=True, null=True)

    # For USER_PASS_HOST services (e.g. OwnCloud)
    service_host = models.URLField(blank=True, null=True)

    # For S3_LIKE services (e.g. ... S3)
    access_key = models.CharField(blank=True, null=True)
    secret_key = models.CharField(blank=True, null=True)

    # For OAUTH2 services
    oauth_access_token = models.CharField(blank=True, null=True)
    oauth2_refresh_token = models.CharField(blank=True, null=True)
    oauth2_refresh_date = models.DateTimeField(blank=True, null=True)
    oauth2_refresh_expiration = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "External Credentials"
        verbose_name_plural = "External Credentials"
        app_label = "addon_service"

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        self._validate_credentials()

    def _validate_credentials(self):
        assigned_fields = {
            field_name
            for field_name in _CREDENTIALS_VALUE_FIELDS
            if getattr(self, field_name, None)
        }
        required_fields = set()
        match self.credentials_issuer.credentials_format:
            case CredentialsFormats.OAUTH2:
                required_fields = (
                    {"oauth_access_token"} if not self.state_token else set()
                )
            case CredentialsFormats.S3_LIKE:
                required_fields = {"access_key", "secret_key"}
            case CredentialsFormats.USER_PASS:
                required_fields = {"user_name", "pwd"}
            case CredentialsFormats.USER_PASS_HOST:
                required_fields = {"user_name", "pwd", "service_host"}
            case _:
                raise ValueError("CredentialsIssuer has unsupported credentials_format")

        if assigned_fields != required_fields:
            raise InvalidCredentials(
                credentials_issuer=self.credentials_issuer,
                missing_fields=required_fields - assigned_fields,
                extra_fields=assigned_fields - required_fields,
            )
        return True
