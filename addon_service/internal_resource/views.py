from rest_framework_json_api.views import RelationshipView

from addon_service.common.base_viewset import CRUDViewSet
from addon_service.models import ConfiguredStorageAddon

from .models import InternalResource
from .serializers import InternalResourceSerializer


class InternalResourceViewSet(CRUDViewSet):  # TODO: read-only
    queryset = InternalResource.objects
    serializer_class = InternalResourceSerializer
    resource_name = 'internal-resources'
    # TODO: permissions_classes


class ConfiguredStorageAddonsView(RelationshipView):
    queryset = ConfiguredStorageAddon.objects
