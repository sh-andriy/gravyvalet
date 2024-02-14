from .models import UserReference
from .serializers import UserReferenceSerializer

from addon_service.common.permissions import SessionUserIsAccountOwner
from addon_service.common.viewsets import RetrieveOnlyViewSet


class UserReferenceViewSet(RetrieveOnlyViewSet):
    queryset = UserReference.objects.all()
    serializer_class = UserReferenceSerializer
    permissions = [SessionUserIsAccountOwner]
