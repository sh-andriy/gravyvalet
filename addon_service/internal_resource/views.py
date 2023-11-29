from rest_framework_json_api.views import (
    ModelViewSet,
    RelationshipView,
)

from .models import InternalResource
from .serializers import InternalResourceSerializer


class InternalResourceViewSet(ModelViewSet):  # TODO: read-only
    queryset = InternalResource.objects.all()
    serializer_class = InternalResourceSerializer
    # TODO: permissions_classes


class InternalResourceRelationshipView(RelationshipView):
    queryset = InternalResource.objects.all()
    resource_name = InternalResourceSerializer.Meta.resource_name
