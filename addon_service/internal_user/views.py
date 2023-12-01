from rest_framework_json_api.views import ModelViewSet

from .models import InternalUser
from .serializers import InternalUserSerializer


class InternalUserViewSet(ModelViewSet):  # TODO: read-only
    queryset = InternalUser.objects.all()
    serializer_class = InternalUserSerializer
    # TODO: permissions_classes
