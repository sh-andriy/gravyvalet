from addon_service.common.permissions import (
    SessionUserCanViewReferencedResource,
    SessionUserIsReferencedResourceAdmin,
)
from addon_service.common.viewsets import RetrieveWriteViewSet

from .models import ConfiguredStorageAddon
from .serializers import ConfiguredStorageAddonSerializer


class ConfiguredStorageAddonViewSet(RetrieveWriteViewSet):
    queryset = ConfiguredStorageAddon.objects.all()
    serializer_class = ConfiguredStorageAddonSerializer

    def get_permissions(self):
        if not self.action:
            return super().get_permissions()

        if self.action in ["retrieve", "retrieve_related", "update", "destroy"]:
            return [SessionUserCanViewReferencedResource()]
        elif self.action == "create":
            return [SessionUserIsReferencedResourceAdmin()]
        else:
            raise NotImplementedError("view action permission not implemented")
