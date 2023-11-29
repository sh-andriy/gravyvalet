from rest_framework_json_api.views import (
    ModelViewSet,
    RelationshipView,
)

from .models import ExternalStorageService
from .serializers import ExternalStorageServiceSerializer


class ExternalStorageServiceViewSet(ModelViewSet):
    queryset = ExternalStorageService.objects.all()
    serializer_class = ExternalStorageServiceSerializer
    # TODO: permissions_classes


class ExternalStorageServiceRelationshipView(RelationshipView):
    queryset = ExternalStorageService.objects.all()
