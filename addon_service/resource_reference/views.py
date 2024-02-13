from .models import ResourceReference
from .serializers import ResourceReferenceSerializer

from addon_service.common.viewsets import RetrieveOnlyViewSet

class ResourceReferenceViewSet(RetrieveOnlyViewSet):
    queryset = ResourceReference.objects.all()
    serializer_class = ResourceReferenceSerializer
    # TODO: permissions_classes

