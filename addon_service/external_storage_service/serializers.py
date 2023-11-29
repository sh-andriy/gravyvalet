from rest_framework_json_api import serializers

from addon_service.models import ExternalStorageService


class ExternalStorageServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalStorageService
        fields = [
            "max_concurrent_downloads",
            "max_upload_mb",
            "auth_uri",
        ]
