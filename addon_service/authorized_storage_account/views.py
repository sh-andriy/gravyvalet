from addon_service.common.permissions import (
    IsAuthenticated,
    SessionUserIsOwner,
)
from addon_service.common.viewsets import (
    RetrieveWriteViewSet,
    ViewSetActions,
)

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer


class AuthorizedStorageAccountViewSet(RetrieveWriteViewSet):
    queryset = AuthorizedStorageAccount.objects.all()
    serializer_class = AuthorizedStorageAccountSerializer

    def get_permissions(self):
        _action_enum = ViewSetActions(self.action)
        if _action_enum.is_item_action():
            return [SessionUserIsOwner()]
        if _action_enum == ViewSetActions.CREATE:
            return [IsAuthenticated()]
        raise NotImplementedError(f"unrecognized viewset action '{self.action}'")
