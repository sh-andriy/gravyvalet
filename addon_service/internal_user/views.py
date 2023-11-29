from addon_service.common.base_viewset import CRUDViewSet

from .models import InternalUser
from .serializers import InternalUserSerializer


class InternalUserViewSet(CRUDViewSet):  # TODO: read-only
    queryset = InternalUser.objects
    serializer_class = InternalUserSerializer
    resource_name = "internal-users"
    # TODO: permissions_classes
