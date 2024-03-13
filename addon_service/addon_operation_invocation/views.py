from rest_framework_json_api.views import ModelViewSet

from .models import AddonOperationInvocation
from .serializers import AddonOperationInvocationSerializer


class AddonOperationInvocationViewSet(ModelViewSet):
    queryset = AddonOperationInvocation.objects.all()
    serializer_class = AddonOperationInvocationSerializer
