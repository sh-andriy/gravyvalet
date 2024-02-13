from rest_framework_json_api.views import ModelViewSet

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer

from addon_service.common.viewsets import RetrieveWriteViewSet

class AuthorizedStorageAccountViewSet(RetrieveWriteViewSet):
    queryset = AuthorizedStorageAccount.objects.all()
    serializer_class = AuthorizedStorageAccountSerializer
