from addon_service.models import ConfiguredStorageAddon
from rest_framework_json_api import serializers


class ConfiguredStorageAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguredStorageAddon
        fields = [
            'root_folder',
            'authorized_storage_account',
            'internal_resource',
        ]
