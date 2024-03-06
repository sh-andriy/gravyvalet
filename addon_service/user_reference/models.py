from django.db import models
from django.utils import timezone

from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.common.base_model import AddonsServiceBaseModel
from addon_service.configured_storage_addon.models import ConfiguredStorageAddon


class UserReference(AddonsServiceBaseModel):
    user_uri = models.URLField(unique=True, db_index=True, null=False)
    disabled = models.DateTimeField(null=True, blank=True)

    @property
    def authorized_storage_accounts(self):
        return AuthorizedStorageAccount.objects.filter(
            external_account__owner=self,
        )

    @property
    def configured_storage_addons(self):
        return ConfiguredStorageAddon.objects.filter(
            base_account__external_account__owner=self,
        )

    class Meta:
        verbose_name = "User Reference"
        verbose_name_plural = "User References"
        app_label = "addon_service"

    class JSONAPIMeta:
        resource_name = "user-references"

    @property
    def owner_reference(self):
        return self.user_uri

    def _delete(self, using=None, keep_parents=False):
        """
        For preventing hard deletes use deactivate instead.
        """
        self.disabled = timezone.now()
        self.save()

    def deactivate(self):
        self._delete()

    def delete(self):
        """
        For preventing hard deletes use deactivate instead.
        """
        self._delete()

    def reactivate(self):
        # TODO: Logging?
        self.disabled = None
        self.save()

    def merge(self, merge_with):
        """
        This represents the user "being merged into", the "merged_user" is the old account that is deactivated and that
        is handled in a seperate signal.
        """
        # TODO: Logging?
        self.configured_storage_addons.add(*merge_with.configured_storage_addons.add())
