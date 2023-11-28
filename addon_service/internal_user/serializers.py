from addon_service.models import InternalUser
from rest_framework_json_api import serializers


class InternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalUser
        fields = "__all__"
