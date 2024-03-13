from addon_service.common.viewsets import DataclassViewset

from .serializers import AddonOperationSerializer


class AddonOperationViewSet(DataclassViewset):
    serializer_class = AddonOperationSerializer
