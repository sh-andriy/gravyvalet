from django.core.exceptions import ValidationError

from addon_service.common.enums.validators import _validate_enum_value

from .known import KnownAddonImps


def validate_storage_imp(value):
    _validate_enum_value(KnownAddonImps, value)
    imp = KnownAddonImps(value)
    if not imp.is_storage_imp:
        raise ValidationError(f"{imp.name} does not implement the StorageProtocol")
