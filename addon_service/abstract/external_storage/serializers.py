from rest_framework_json_api import serializers

from addon_service.common.credentials_formats import CredentialsFormats
from addon_service.common.enum_serializers import EnumNameChoiceField


class ExternalServiceSerializer(serializers.HyperlinkedModelSerializer):

    credentials_format = EnumNameChoiceField(
        enum_cls=CredentialsFormats, read_only=True
    )

    included_serializers = {
        "addon_imp": "addon_service.serializers.AddonImpSerializer",
    }

    class Meta:
        fields = [
            "id",
            "addon_imp",
            "auth_uri",
            "credentials_format",
            "max_concurrent_downloads",
            "max_upload_mb",
            "display_name",
            "url",
            "wb_key",
        ]
