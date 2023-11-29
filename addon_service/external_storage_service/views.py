from addon_service.common.base_viewset import CRUDViewSet

from .models import ExternalStorageService
from .serializers import ExternalStorageServiceSerializer


class ExternalStorageServiceViewSet(CRUDViewSet):
    queryset = ExternalStorageService.objects
    serializer_class = ExternalStorageServiceSerializer
    resource_name = "external-storage-services"
    # TODO: permissions_classes
