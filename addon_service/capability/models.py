from addon_service.common.enums import IntEnumForEnum
from addon_toolkit.storage import StorageCapability


__all__ = ("IntStorageCapability",)


class IntStorageCapability(IntEnumForEnum, base_enum=StorageCapability):
    ACCESS = 1
    UPDATE = 2
