from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from addon_service.models import (
    ConfiguredStorageAddon,
    InternalResource,
)


RESOURCE_NAME = ConfiguredStorageAddon.JSONAPIMeta.resource_name


class ConfiguredStorageAddonSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name=f"{RESOURCE_NAME}-detail")
    authorized_storage_account = ResourceRelatedField(
        queryset=ConfiguredStorageAddon.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
        self_link_view_name=f"{RESOURCE_NAME}-relationships",
    )
    internal_resource = ResourceRelatedField(
        queryset=InternalResource.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
        self_link_view_name=f"{RESOURCE_NAME}-relationships",
    )

    included_serializers = {
        "authorized_storage_account": (
            "addon_service.serializers.AuthorizedStorageAccountSerializer"
        ),
        "internal_resource": "addon_service.serializers.InternalResourceSerializer",
    }

    class Meta:
        model = ConfiguredStorageAddon
        fields = [
            "url",
            "root_folder",
            "authorized_storage_account",
            "internal_resource",
        ]
