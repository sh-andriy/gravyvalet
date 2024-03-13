from rest_framework_json_api import serializers
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.addon_imp.models import AddonImpModel
from addon_service.common import view_names
from addon_service.common.serializer_fields import DataclassRelatedDataField
from addon_service.models import ExternalStorageService


RESOURCE_TYPE = get_resource_type_from_model(ExternalStorageService)


class ExternalStorageServiceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=view_names.detail_view(RESOURCE_TYPE)
    )
    addon_imp = DataclassRelatedDataField(
        dataclass_model=AddonImpModel,
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
    )
    included_serializers = {
        "addon_imp": "addon_service.serializers.AddonImpSerializer",
    }

    class Meta:
        model = ExternalStorageService
        fields = [
            "url",
            "max_concurrent_downloads",
            "max_upload_mb",
            "auth_uri",
            "addon_imp",
        ]
