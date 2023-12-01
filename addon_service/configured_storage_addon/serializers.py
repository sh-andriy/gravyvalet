from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.models import (
    ConfiguredStorageAddon,
    InternalResource,
)


RESOURCE_NAME = get_resource_type_from_model(ConfiguredStorageAddon)


class ConfiguredStorageAddonSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name=f"{RESOURCE_NAME}-detail")
    authorized_storage_account = ResourceRelatedField(
        queryset=ConfiguredStorageAddon.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    internal_resource = ResourceRelatedField(
        queryset=InternalResource.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
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
