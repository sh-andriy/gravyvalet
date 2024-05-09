from django.core.exceptions import ValidationError

from addon_service.common.invocation import InvocationStatus
from addon_toolkit import AddonCapabilities


# helper for enum-based validators
def _validate_enum_value(enum_cls, value, excluded_members=None):
    try:
        member = enum_cls(value)
    except ValueError:
        raise ValidationError(f'no value "{value}" in {enum_cls}')
    if excluded_members and member in excluded_members:
        raise ValidationError(
            f'"{member.name}" is not a supported value for this field'
        )


###
# validators for specific controlled vocabs


def validate_addon_capability(value):
    _validate_enum_value(AddonCapabilities, value)


def validate_invocation_status(value):
    _validate_enum_value(InvocationStatus, value)
