from django.db import models

from addon_service.addon_imp.instantiation import get_storage_addon_instance
from addon_service.authorized_account.models import AuthorizedAccount
from addon_service.external_storage_service import ExternalStorageService
from addon_toolkit.interfaces.storage import StorageConfig


class AuthorizedStorageAccount(AuthorizedAccount):
    """Model for descirbing a user's account on an ExternalStorageService.

    This model collects all of the information required to actually perform remote
    operations against the service and to aggregate accounts under a known user.
    """

    default_root_folder = models.CharField(blank=True)

    external_storage_service = models.ForeignKey(
        "addon_service.ExternalStorageService",
        on_delete=models.CASCADE,
        related_name="authorized_storage_accounts",
    )

    class Meta:
        verbose_name = "Authorized Storage Account"
        verbose_name_plural = "Authorized Storage Accounts"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "authorized-storage-accounts"

    @property
    def external_service(self) -> ExternalStorageService:
        return self.external_storage_service

    async def execute_post_auth_hook(self, auth_extras: dict | None = None):
        imp = await get_storage_addon_instance(
            self.imp_cls, self, self.storage_imp_config
        )
        self.external_account_id = await imp.get_external_account_id(auth_extras or {})
        await self.asave()

    @property
    def storage_imp_config(self) -> StorageConfig:
        return StorageConfig(
            max_upload_mb=self.external_service.max_upload_mb,
            external_api_url=self.api_base_url,
            connected_root_id=self.default_root_folder,
            external_account_id=self.external_account_id,
        )
