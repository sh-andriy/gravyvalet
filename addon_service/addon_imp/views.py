from addon_service.common.viewsets import DataclassViewset

from .serializers import AddonImpSerializer


class AddonImpViewSet(DataclassViewset):
    serializer_class = AddonImpSerializer
    permission_classes: list[
        type
    ] = []  # addon implementations are public (and read-only)
