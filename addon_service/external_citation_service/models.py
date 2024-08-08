from django.db import models

from addon_service.abstract.external_storage.models import ExternalService


class ExternalCitationService(ExternalService):
    int_addon_imp = models.IntegerField(
        null=False,
        verbose_name="Addon implementation",
    )
    wb_key = models.CharField(null=False, blank=True, default="")
    oauth1_client_config = models.ForeignKey(
        "addon_service.OAuth1ClientConfig",
        on_delete=models.SET_NULL,
        related_name="external_citation_services",
        null=True,
        blank=True,
    )

    oauth2_client_config = models.ForeignKey(
        "addon_service.OAuth2ClientConfig",
        on_delete=models.SET_NULL,
        related_name="external_citation_services",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "External Citation Service"
        verbose_name_plural = "External Citation Services"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "external-citation-services"
