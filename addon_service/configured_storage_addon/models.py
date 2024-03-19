from django.db import models

from addon_service.common.base_model import AddonsServiceBaseModel


class ActiveUserManager(models.Manager):
    """
    Only returned active users, not ones that are disabled.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(base_account__external_account__owner__disabled__isnull=True)
        )


class ConfiguredStorageAddon(AddonsServiceBaseModel):
    objects = ActiveUserManager()

    root_folder = models.CharField()

    base_account = models.ForeignKey(
        "addon_service.AuthorizedStorageAccount",
        on_delete=models.CASCADE,
        related_name="configured_storage_addons",
    )
    authorized_resource = models.ForeignKey(
        "addon_service.ResourceReference",
        on_delete=models.CASCADE,
        related_name="configured_storage_addons",
    )

    class Meta:
        verbose_name = "Configured Storage Addon"
        verbose_name_plural = "Configured Storage Addons"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "configured-storage-addons"

    @property
    def account_owner(self):
        return self.base_account.external_account.owner

    @property
    def owner_reference(self):
        return self.base_account.external_account.owner.user_uri

    @property
    def resource_uri(self):
        return self.authorized_resource.resource_uri
