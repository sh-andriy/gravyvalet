from addon_service.capability.models import IntStorageCapability
from addon_service.common.enums.serializers import DualEnumsListField
from addon_toolkit.storage import StorageCapability


class StorageCapabilityListField(
    DualEnumsListField,
    external_enum=StorageCapability,
    internal_enum=IntStorageCapability,
):
    pass
