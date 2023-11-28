from addon_service.models import InternalResource
from rest_framework_json_api import serializers


class InternalResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = InternalResource
        fields = [
            'resource_uri',
            'configured_storage_addons',
        ]
