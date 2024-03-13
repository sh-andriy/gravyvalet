import enum

from rest_framework_json_api import serializers


class _BaseEnumNameChoiceField(serializers.ChoiceField):
    enum_cls: type[enum.Enum]

    def __init__(self, enum_cls: type[enum.Enum], **kwargs):
        assert issubclass(enum_cls, enum.Enum) and (enum_cls is not enum.Enum)
        self.enum_cls = enum_cls
        super().__init__(
            **kwargs,
            choices=(_member.name for _member in enum_cls),
        )


class EnumNameChoiceField(_BaseEnumNameChoiceField):
    def to_internal_value(self, data) -> enum.Enum:
        _name = super().to_internal_value(data)
        return self.enum_cls[_name]

    def to_representation(self, value: enum.Enum):
        return super().to_representation(value).name


class EnumNameMultipleChoiceField(
    _BaseEnumNameChoiceField, serializers.MultipleChoiceField
):
    def to_internal_value(self, data) -> list[enum.Enum]:
        _names: set = super().to_internal_value(data)
        return [self.enum_cls[_name] for _name in _names]

    def to_representation(self, value):
        _member_list = super().to_representation(value)
        return [_member.name for _member in _member_list]
