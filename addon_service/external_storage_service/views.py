from rest_framework_json_api.views import ReadOnlyViewSet

from .models import ExternalStorageService
from .serializers import ExternalStorageServiceSerializer


class ExternalStorageServiceViewSet(ReadOnlyViewSet):
    queryset = ExternalStorageService.objects.all()
    serializer_class = ExternalStorageServiceSerializer
    # TODO: permissions_classes
