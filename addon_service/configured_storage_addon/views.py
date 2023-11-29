from rest_framework_json_api.views import (
    ModelViewSet,
    RelationshipView,
)

from .models import ConfiguredStorageAddon
from .serializers import ConfiguredStorageAddonSerializer


class ConfiguredStorageAddonViewSet(ModelViewSet):
    queryset = ConfiguredStorageAddon.objects.all()
    serializer_class = ConfiguredStorageAddonSerializer
    # TODO: permissions_classes


class ConfiguredStorageAddonRelationshipView(RelationshipView):
    queryset = ConfiguredStorageAddon.objects.all()
