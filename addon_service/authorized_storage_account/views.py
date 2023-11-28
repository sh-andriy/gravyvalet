from addon_service.common.base_viewset import CRUDViewSet

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer


class AuthorizedStorageAccountViewSet(CRUDViewSet):
    queryset = AuthorizedStorageAccount.objects
    serializer_class = AuthorizedStorageAccountSerializer
    resource_name = 'authorized-storage-accounts'
    # TODO: permissions_classes
