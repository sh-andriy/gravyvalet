import enum
from typing import ClassVar


def same_enum_names(enum_a: type[enum.Enum], enum_b: type[enum.Enum]) -> bool:
    # ensure enums have same names
    _names_a = {_item.name for _item in enum_a}
    _names_b = {_item.name for _item in enum_b}
    return _names_a == _names_b


class IntEnumForEnum(enum.IntEnum):
    __base_enum: ClassVar[type[enum.Enum]]

    def __init_subclass__(cls, /, base_enum: type[enum.Enum], **kwargs):
        super().__init_subclass__(**kwargs)
        assert same_enum_names(base_enum, cls)
        cls.__base_enum = base_enum

    @classmethod
    def to_int(cls, base_enum_member):
        return cls[base_enum_member.name]

    @classmethod
    def as_django_choices(cls):
        return [(int(_item), _item.name) for _item in cls]

    def to_base_enum(self) -> enum.Enum:
        return self.__base_enum[self.name]
