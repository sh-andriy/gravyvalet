from rest_framework import serializers as drf_serializers
from rest_framework_json_api import serializers as json_api_serializers


class ReadOnlyResourceRelatedField(
    json_api_serializers.ResourceRelatedField, drf_serializers.ReadOnlyField
):
    pass
