from rest_framework_json_api.views import ModelViewSet

from .models import InternalResource
from .serializers import InternalResourceSerializer


class InternalResourceViewSet(ModelViewSet):  # TODO: read-only
    queryset = InternalResource.objects.all()
    serializer_class = InternalResourceSerializer
    # TODO: permissions_classes
