from addon_service.common.base_viewset import CRUDViewSet

from .models import ConfiguredStorageAddon
from .serializers import ConfiguredStorageAddonSerializer


class ConfiguredStorageAddonViewSet(CRUDViewSet):
    queryset = ConfiguredStorageAddon.objects
    serializer_class = ConfiguredStorageAddonSerializer
    resource_name = "configured-storage-addons"
    # TODO: permissions_classes
