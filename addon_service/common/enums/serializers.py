import enum
from typing import ClassVar

from rest_framework_json_api import serializers

from addon_service.common.enums import same_enum_names


class DualEnumsListField(serializers.MultipleChoiceField):
    """use one enum in your database and another in your api!"""

    __internal_enum: ClassVar[type[enum.Enum]]
    __external_enum: ClassVar[type[enum.Enum]]

    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            choices={  # valid serialized values come from the external enum
                _external_member.value for _external_member in self.__external_enum
            },
        )

    def __init_subclass__(
        cls,
        /,
        internal_enum: type[enum.Enum],
        external_enum: type[enum.Enum],
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)
        assert same_enum_names(internal_enum, external_enum)
        cls.__internal_enum = internal_enum
        cls.__external_enum = external_enum

    def to_internal_value(self, data) -> list[enum.Enum]:
        _names: set = super().to_internal_value(data)
        return [self._to_internal_enum_member(_name) for _name in _names]

    def to_representation(self, value):
        _member_list = super().to_representation(value)
        return {self._to_external_enum_value(_member) for _member in _member_list}

    def _to_internal_enum_member(self, external_value) -> enum.Enum:
        _external_member = self.__external_enum(external_value)
        return self.__internal_enum[_external_member.name]

    def _to_external_enum_value(self, internal_value: enum.Enum):
        _internal_member = self.__internal_enum(internal_value)
        _external_member = self.__external_enum[_internal_member.name]
        return _external_member.value
