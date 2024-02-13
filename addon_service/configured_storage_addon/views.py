from .models import ConfiguredStorageAddon
from .serializers import ConfiguredStorageAddonSerializer

from addon_service.common.viewsets import RetrieveWriteViewSet

class ConfiguredStorageAddonViewSet(RetrieveWriteViewSet):
    queryset = ConfiguredStorageAddon.objects.all()
    serializer_class = ConfiguredStorageAddonSerializer
