from http import HTTPMethod

from rest_framework.decorators import action
from rest_framework.response import Response

from addon_service.common.permissions import (
    IsAuthenticated,
    OSFOnly,
    SessionUserCanViewReferencedResource,
    SessionUserIsOwner,
    SessionUserIsReferencedResourceAdmin,
)
from addon_service.common.viewsets import RetrieveWriteViewSet
from addon_service.credentials import utils as credentials_utils

from .models import ConfiguredStorageAddon
from .serializers import (
    ConfiguredStorageAddonSerializer,
    WaterButlerConfigurationSerializer,
)
from .utils import serialize_waterbutler_settings


class ConfiguredStorageAddonViewSet(RetrieveWriteViewSet):
    queryset = ConfiguredStorageAddon.objects.active()
    serializer_class = ConfiguredStorageAddonSerializer

    def get_permissions(self):
        match self.action:
            case "retrieve" | "retrieve_related":
                return [IsAuthenticated(), SessionUserCanViewReferencedResource()]
            case "partial_update" | "update" | "destroy":
                return [IsAuthenticated(), SessionUserIsOwner()]
            case "create":
                return [IsAuthenticated(), SessionUserIsReferencedResourceAdmin()]
            case "get_wb_config":
                return [OSFOnly()]
            case None:
                return super().get_permissions()
            case _:
                raise NotImplementedError(
                    f"no permission implemented for action '{self.action}'"
                )

    @action(
        detail=True,
        methods=[HTTPMethod.GET],
        url_name="waterbutler-config",
        url_path="waterbutler-config",
        permission_classes=[OSFOnly],
    )
    def get_wb_config(self, request, pk=None):
        addon = self.get_object()
        serializer_data = {
            "credentials": credentials_utils.format_credentials_for_waterbutler(
                addon.credentials
            ),
            "settings": serialize_waterbutler_settings(addon),
        }
        serialized_config = WaterButlerConfigurationSerializer(data=serializer_data)
        serialized_config.is_valid()
        return Response(serialized_config.data)
