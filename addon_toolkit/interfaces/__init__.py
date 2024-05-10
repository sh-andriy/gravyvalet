import enum
import typing

# note: addon_toolkit.interfaces is downstream from addon_toolkit
from addon_toolkit import (
    AddonImp,
    exceptions,
)

from .storage import StorageAddonImp


__all__ = (
    "AddonInterfaces",
    "StorageAddonImp",
)


class AddonInterfaces(enum.Enum):
    STORAGE = StorageAddonImp

    # type annotation for `value` (enforced by __init__)
    value: type[AddonImp]

    def __init__(self, value: typing.Any) -> None:
        if not issubclass(value, AddonImp):
            raise exceptions.NotAnImp(value)

    @staticmethod
    def for_concrete_imp(imp_cls: type[AddonImp]) -> "AddonInterfaces":
        if imp_cls in AddonInterfaces:
            raise exceptions.ImpTooAbstract(imp_cls)
        _inherited_interfaces = [
            _interface_member
            for _interface_member in AddonInterfaces
            if issubclass(imp_cls, _interface_member.value)
        ]
        match len(_inherited_interfaces):
            case 1:
                return _inherited_interfaces[0]
            case 0:
                raise exceptions.NotAnImp(imp_cls)
            case _:
                raise exceptions.ImpHasTooManyJobs(imp_cls, _inherited_interfaces)
