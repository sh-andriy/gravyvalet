from addon_service.common.permissions import (
    SessionUserIsOwner,
    SessionUserMayAccessInvocation,
    SessionUserMayInvokeThruAddon,
)
from addon_service.common.viewsets import RetrieveWriteViewSet

from .models import AddonOperationInvocation
from .serializers import AddonOperationInvocationSerializer


class AddonOperationInvocationViewSet(RetrieveWriteViewSet):
    queryset = AddonOperationInvocation.objects.all()
    serializer_class = AddonOperationInvocationSerializer

    def get_permissions(self) -> list[type]:
        match self.action:
            case "retrieve" | "retrieve_related":
                return [SessionUserMayAccessInvocation()]
            case "partial_update" | "update" | "destroy":
                return [SessionUserIsOwner()]
            case "create":
                return [SessionUserMayInvokeThruAddon()]
            case _:
                raise NotImplementedError(
                    "no permission implemented for action '{self.action}'"
                )
