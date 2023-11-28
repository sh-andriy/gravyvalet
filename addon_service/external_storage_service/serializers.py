from addon_service.models import ExternalStorageService
from rest_framework_json_api import serializers


class ExternalStorageService(serializers.ModelSerializer):
    class Meta:
        model = ExternalStorageService
        fields = "__all__"
