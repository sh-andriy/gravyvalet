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


class InternalUserRelationshipView(RelationshipView):
    queryset = InternalUser.objects.all()
