from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from addon_service.common.base_model import AddonsServiceBaseModel

from .validators import ensure_shared_client


class OAuth2ClientConfig(AddonsServiceBaseModel):
    """
    Model for storing attributes that are required for managing
    OAuth2 credentials exchanges with an ExternalService on behalf
    of a registered client (e.g. the OSF)
    """

    # The base uri for initiating OAuth2 credentials exchanges
    auth_uri = models.URLField(null=False)
    # The registered ID of the OAuth client
    client_id = models.CharField(null=True)
    client_secret = models.CharField(null=True)

    class Meta:
        verbose_name = "OAuth2 Client Config"
        verbose_name_plural = "OAuth2 Client Configs"
        app_label = "addon_service"


class OAuth2TokenMetadata(AddonsServiceBaseModel):
    """
    Model for storing attribute that are related to an OAuth2 Access Token
    but are not actually used for authenticating with the external service.
    """

    # The token used to identify the initiatl auth request with the external service
    state_token = models.CharField(null=True, blank=True, db_index=True)
    # The unique ID of the user on the external sservice
    user_id = models.CharField(null=True, blank=True)
    # The token used to exchange access tokens
    refresh_token = models.CharField(null=True, blank=True, db_index=True)
    # The expiration time of the access token stored in Credentials
    access_token_expiration = models.DateTimeField(null=True, blank=True)
    # The scopes associated with the access token stored in Credentials
    authorized_scopes = ArrayField(models.CharField(), null=False)

    @property
    def linked_accounts(self):
        return tuple(self.authorized_storage_accounts.all())

    @property
    def client_details(self):
        return self.linked_accounts[0].external_service.oauth2_client_details

    def update_from_token_endpoint_response(self, response_json):
        # State token should never be set following a successful token exchange
        self.state_token = None
        self.refresh_token = response_json.get("refresh_token")
        self.access_token_expiration = timezone.now() + timedelta(
            seconds=response_json["expires_in"]
        )
        if "scopes" in response_json:
            self.authorized_scopes = response_json["scopes"]
        self.save()

    def clean_fields(self, *args, **kwargs):
        super().clean_fields(*args, **kwargs)
        if not self.pk:
            return

        ensure_shared_client(self)
        if self.state_token and self.refresh_token:
            raise ValidationError(
                "Error on OAuth2 Flow: state token and refresh token both present."
            )
        if not (self.state_token or self.refresh_token):
            raise ValidationError(
                "Error in OAuth2 Flow: Neither state token nor refresh token present."
            )

    class Meta:
        verbose_name = "OAuth2 Token Metadata"
        verbose_name_plural = "OAuth2 Token Metadata"
        app_label = "addon_service"
        constraints = [
            models.UniqueConstraint(fields=["state_token"], name="unique state token")
        ]
