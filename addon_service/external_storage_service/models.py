from django.db import models

from addon_service.addon_imp.known import get_imp_by_number
from addon_service.addon_imp.models import AddonImpModel
from addon_service.common.base_model import AddonsServiceBaseModel
from addon_service.common.enums.validators import validate_storage_imp_number


class ExternalStorageService(AddonsServiceBaseModel):
    int_addon_imp = models.IntegerField(
        null=False,
        validators=[validate_storage_imp_number],
    )
    max_concurrent_downloads = models.IntegerField(null=False)
    max_upload_mb = models.IntegerField(null=False)

    credentials_issuer = models.ForeignKey(
        "addon_service.CredentialsIssuer",
        on_delete=models.CASCADE,
        related_name="external_storage_services",
    )

    class Meta:
        verbose_name = "External Storage Service"
        verbose_name_plural = "External Storage Services"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "external-storage-services"

    @property
    def addon_imp(self) -> AddonImpModel:
        return AddonImpModel(get_imp_by_number(self.int_addon_imp))

    @property
    def auth_uri(self):
        return self.credentials_issuer.auth_uri

    @property
    def credentials_format(self):
        return self.credentials_issuer.credentials_format
