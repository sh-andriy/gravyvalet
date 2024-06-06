from http import HTTPMethod

from rest_framework.decorators import action
from rest_framework.response import Response

from addon_service.common.credentials_formats import CredentialsFormats
from addon_service.common.permissions import (
    IsAuthenticated,
    IsValidHMACSignedRequest,
    SessionUserCanViewReferencedResource,
    SessionUserIsOwner,
    SessionUserMayConnectAddon,
)
from addon_service.common.viewsets import RetrieveWriteDeleteViewSet
from addon_service.common.waterbutler_compat import WaterButlerConfigurationSerializer

from .models import ConfiguredStorageAddon
from .serializers import ConfiguredStorageAddonSerializer


class ConfiguredStorageAddonViewSet(RetrieveWriteDeleteViewSet):
    queryset = ConfiguredStorageAddon.objects.active()
    serializer_class = ConfiguredStorageAddonSerializer

    def get_permissions(self):
        match self.action:
            case "retrieve" | "retrieve_related":
                return [IsAuthenticated(), SessionUserCanViewReferencedResource()]
            case "partial_update" | "update" | "destroy":
                return [IsAuthenticated(), SessionUserIsOwner()]
            case "create":
                return [IsAuthenticated(), SessionUserMayConnectAddon()]
            case "get_wb_config":
                return [IsValidHMACSignedRequest()]
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
    )
    def get_wb_config(self, request, pk=None):
        addon = self.get_object()
        if addon.external_service.credentials_format is CredentialsFormats.OAUTH2:
            addon.base_account.refresh_oauth_access_token__blocking()
        self.resource_name = "waterbutler-config"  # for the jsonapi resource type
        return Response(WaterButlerConfigurationSerializer(addon).data)
