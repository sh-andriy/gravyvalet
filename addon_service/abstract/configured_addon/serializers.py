from rest_framework_json_api import serializers

from addon_service.common.enum_serializers import EnumNameMultipleChoiceField
from addon_toolkit import AddonCapabilities


class ConfiguredAddonSerializer(serializers.HyperlinkedModelSerializer):

    connected_capabilities = EnumNameMultipleChoiceField(enum_cls=AddonCapabilities)
    connected_operation_names = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    authorized_resource_uri = serializers.CharField(
        required=False, source="resource_uri", write_only=True
    )

    class Meta:
        fields = [
            "id",
            "url",
            "display_name",
            "base_account",
            "authorized_resource",
            "authorized_resource_uri",
            "connected_capabilities",
            "connected_operations",
            "connected_operation_names",
        ]
