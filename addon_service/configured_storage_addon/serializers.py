from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.models import (
    AuthorizedStorageAccount,
    ConfiguredStorageAddon,
    ResourceReference,
)


RESOURCE_NAME = get_resource_type_from_model(ConfiguredStorageAddon)


class AuthorizedResourceField(ResourceRelatedField):
    def to_internal_value(self, data):
        resource_reference, _ = ResourceReference.objects.get_or_create(
            resource_uri=data["id"]
        )
        return resource_reference


class ConfiguredStorageAddonSerializer(serializers.HyperlinkedModelSerializer):
    root_folder = serializers.CharField(required=False)
    url = serializers.HyperlinkedIdentityField(view_name=f"{RESOURCE_NAME}-detail")
    base_account = ResourceRelatedField(
        queryset=AuthorizedStorageAccount.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    authorized_resource = AuthorizedResourceField(
        queryset=ResourceReference.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )

    included_serializers = {
        "base_account": (
            "addon_service.serializers.AuthorizedStorageAccountSerializer"
        ),
        "authorized_resource": "addon_service.serializers.ResourceReferenceSerializer",
    }

    class Meta:
        model = ConfiguredStorageAddon
        fields = [
            "url",
            "root_folder",
            "base_account",
            "authorized_resource",
        ]