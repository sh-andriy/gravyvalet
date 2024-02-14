from rest_framework_json_api.views import ModelViewSet

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer

from addon_service.common.permissions import IsAuthenticated, SessionUserIsAccountOwner
from addon_service.common.viewsets import RetrieveWriteViewSet

class AuthorizedStorageAccountViewSet(RetrieveWriteViewSet):
    queryset = AuthorizedStorageAccount.objects.all()
    serializer_class = AuthorizedStorageAccountSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'destroy']:
            return [SessionUserIsAccountOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            raise RuntimeError #todo, better exception
