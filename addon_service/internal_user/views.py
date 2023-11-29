from rest_framework_json_api.views import (
    ModelViewSet,
    RelationshipView,
)

from .models import InternalUser
from .serializers import InternalUserSerializer


class InternalUserViewSet(ModelViewSet):  # TODO: read-only
    queryset = InternalUser.objects.all()
    serializer_class = InternalUserSerializer
    # TODO: permissions_classes

    def get_queryset(self):
        _queryset = super().get_queryset()
        _asa_pk = self.kwargs.get("authorizedstorageaccount_pk")
        if _asa_pk is not None:
            _queryset = _queryset.filter(external_accounts__owner__pk=_asa_pk)
        return _queryset


class InternalUserRelationshipView(RelationshipView):
    queryset = InternalUser.objects.all()
    resource_name = InternalUserSerializer.Meta.resource_name
