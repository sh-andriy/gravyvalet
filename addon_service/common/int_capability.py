import enum
from typing import ClassVar

from addon_toolkit.categories.storage import StorageCapability


__all__ = ("IntStorageCapability",)


class _IntEnumForEnum(enum.IntEnum):
    __base_enum: ClassVar[type[enum.Enum]]

    def __init_subclass__(cls, /, base_enum: type[enum.Enum], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__base_enum = base_enum
        _base_names = {_item.name for _item in base_enum}
        _int_names = {_item.name for _item in cls}
        assert _base_names == _int_names

    @classmethod
    def to_int(cls, base_enum_member):
        return cls[base_enum_member.name]

    @classmethod
    def as_django_choices(cls):
        return [(int(_item), _item.name) for _item in cls]

    def to_base_enum(self) -> enum.Enum:
        return self.__base_enum[self.name]


class IntStorageCapability(_IntEnumForEnum, base_enum=StorageCapability):
    ACCESS = 1
    BROWSE = 2
    UPDATE = 3
    COMMIT = 4
