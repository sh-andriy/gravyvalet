import enum

from rest_framework_json_api import serializers

from addon_service.capability.models import (
    IntStorageCapability,
    StorageCapability,
)


class EnumsMultipleChoiceField(serializers.MultipleChoiceField):
    __internal_enum: type[enum.Enum]
    __external_enum: type[enum.Enum]

    def __init__(self, /, internal_enum, external_enum, **kwargs):
        _choices = {_external_member.value for _external_member in external_enum}
        super().__init__(**kwargs, choices=_choices)
        self.__internal_enum = internal_enum
        self.__external_enum = external_enum

    def to_internal_value(self, data):
        _names = super().to_internal_value(data)
        return {self._to_internal_enum_member(_name) for _name in _names}

    def to_representation(self, value):
        _member_list = super().to_representation(value)
        return {self._to_external_enum_value(_member) for _member in _member_list}

    def _to_internal_enum_member(self, external_value):
        _external_member = self.__external_enum(external_value)
        return self.__internal_enum[_external_member.name]

    def _to_external_enum_value(self, internal_value):
        _internal_member = self.__internal_enum(internal_value)
        _external_member = self.__external_enum[_internal_member.name]
        return _external_member.value


def StorageCapabilityField(**kwargs):
    return EnumsMultipleChoiceField(
        external_enum=StorageCapability,
        internal_enum=IntStorageCapability,
        **kwargs,
    )
