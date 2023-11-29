from rest_framework_json_api.views import (
    ModelViewSet,
    RelationshipView,
)

from .models import AuthorizedStorageAccount
from .serializers import AuthorizedStorageAccountSerializer


class AuthorizedStorageAccountViewSet(ModelViewSet):
    queryset = AuthorizedStorageAccount.objects.all()
    serializer_class = AuthorizedStorageAccountSerializer
    # TODO: permissions_classes

    def get_queryset(self):
        _queryset = super().get_queryset()
        _csa_pk = self.kwargs.get("configuredstorageaddon_pk")
        if _csa_pk is not None:
            _queryset = _queryset.filter(configured_storage_addons__pk=_csa_pk)
        return _queryset


class AuthorizedStorageAccountRelationshipView(RelationshipView):
    queryset = AuthorizedStorageAccount.objects.all()
