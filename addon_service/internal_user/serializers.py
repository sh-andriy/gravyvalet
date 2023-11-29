from rest_framework_json_api import serializers

from addon_service.models import InternalUser


class InternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalUser
        fields = "__all__"
