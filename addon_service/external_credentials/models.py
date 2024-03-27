from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel
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
    user_name = models.CharField(blank=True, null=True)
    pwd = models.CharField(blank=True, null=True)

    # For USER_PASS_HOST services (e.g. OwnCloud)
    service_host = models.CharField(blank=True, null=True)

    # For S3_LIKE services (e.g. ... S3)
    access_key = models.CharField(blank=True, null=True)
    secret_key = models.CharField(blank=True, null=True)

    # For OAuth 1/2
    oauth_access_token = models.CharField(blank=True, null=True)

    # For OAuth1, this is usually the "oauth_token_secret"
    # For OAuth2, this is not used
    oauth_secret = models.CharField(blank=True, null=True)

    # Used for OAuth2 only
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
        credentials_format = self.credentials_issuer.credentials_format
        required_fields = credentials_format.required_fields
        if assigned_fields != required_fields:
            raise InvalidCredentials(
                credentials_format=credentials_format,
                missing_fields=required_fields - assigned_fields,
                extra_fields=assigned_fields - required_fields,
            )
        return True
