from enum import (
    IntEnum,
    auto,
    unique,
)

from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel


@unique
class OAuth1State(IntEnum):
    START = auto()
    WAITING_FOR_USER_AUTHORISATION = auto()
    READY = auto()


class OAuth1ClientConfig(AddonsServiceBaseModel):
    """
    Model for storing attributes that are required for managing
    OAuth1 credentials exchanges with an ExternalService on behalf
    of a registered client (e.g. the OSF)
    """

    # URI that allows to obtain temporary request token to proceed with user auth
    request_token_url = models.URLField(null=False)
    # URI to which user will be redirected to authenticate
    auth_url = models.URLField(null=False)
    # URI to obtain access token
    access_token_url = models.URLField(null=False)

    client_key = models.CharField(null=True)
    client_secret = models.CharField(null=True)

    class Meta:
        verbose_name = "OAuth1 Client Config"
        verbose_name_plural = "OAuth1 Client Configs"
        app_label = "addon_service"

    def __repr__(self):
        return f'<{self.__class__.__qualname__}(pk="{self.pk}", auth_uri="{self.auth_url}, access_token_url="{self.access_token_url}", request_token_url="{self.request_token_url}", client_key="{self.client_key}")>'

    __str__ = __repr__
