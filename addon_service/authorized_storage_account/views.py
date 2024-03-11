from addon_service.common.permissions import (
    IsAuthenticated,
    SessionUserIsOwner,
)
from addon_service.common.viewsets import RetrieveWriteViewSet

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer


class AuthorizedStorageAccountViewSet(RetrieveWriteViewSet):
    queryset = AuthorizedStorageAccount.objects.all()
    serializer_class = AuthorizedStorageAccountSerializer

    def get_permissions(self):
        if not self.action:
            return super().get_permissions()

        if self.action in ["retrieve", "retrieve_related", "update", "destroy"]:
            return [SessionUserIsOwner()]
        return [IsAuthenticated()]
