from rest_framework_json_api import serializers
from rest_framework_json_api.relations import (
    HyperlinkedRelatedField,
    ResourceRelatedField,
    SerializerMethodResourceRelatedField,
)

from addon_service.models import (
    AuthorizedStorageAccount,
    ConfiguredStorageAddon,
    ExternalStorageService,
    InternalUser,
)


RESOURCE_NAME = "authorized-storage-accounts"


class AuthorizedStorageAccountSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name=f"{RESOURCE_NAME}-detail")
    account_owner = SerializerMethodResourceRelatedField(
        model=InternalUser,
        many=False,
        method_name="_get_account_owner",
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    external_storage_service = ResourceRelatedField(
        queryset=ExternalStorageService.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    configured_storage_addons = HyperlinkedRelatedField(
        many=True,
        queryset=ConfiguredStorageAddon.objects.all(),
        related_link_view_name=f"{RESOURCE_NAME}-related",
        self_link_view_name=f"{RESOURCE_NAME}-relationships",
    )

    included_serializers = {
        "account_owner": "addon_service.serializers.InternalUserSerializer",
        "external_storage_service": (
            "addon_service.serializers.ExternalStorageServiceSerializer"
        ),
        "configured_storage_addons": (
            "addon_service.serializers.ConfiguredStorageAddonSerializer"
        ),
    }

    class Meta:
        model = AuthorizedStorageAccount
        resource_name = RESOURCE_NAME
        fields = [
            "url",
            "account_owner",
            "configured_storage_addons",
            "default_root_folder",
            "external_storage_service",
        ]

    def _get_account_owner(self, instance: AuthorizedStorageAccount):
        return instance.external_account.owner  # TODO: prefetch/select_related
