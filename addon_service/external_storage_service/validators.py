import functools

from addon_service.common.enums.validators import _validate_enum_value

from .enums import ServiceTypes


validate_service_type = functools.partial(_validate_enum_value, ServiceTypes)
