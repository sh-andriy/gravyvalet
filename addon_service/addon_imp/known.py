"""the single static source of truth for addon implementations known to the addon service

import and add new implementations here to make them available in the api
"""

import enum

from addon_imps.storage import box_dot_com
from addon_service.common.enums import enum_names_same_as
from addon_toolkit import AddonImp


if __debug__:
    from addon_imps.storage import my_blarg


__all__ = (
    "get_imp_by_name",
    "get_imp_name",
    "get_imp_by_number",
)


@enum.unique
class KnownAddonImps(enum.Enum):
    """enum with a name for each addon implementation class that should be known to the api"""

    value: type[
        AddonImp
    ]  # type annotation only: all values should be subclasses of AddonImp

    BOX_DOT_COM = box_dot_com.BoxDotComStorageImp

    if __debug__:
        BLARG = my_blarg.MyBlargStorage


@enum.unique
@enum_names_same_as(KnownAddonImps)
class AddonImpNumbers(enum.Enum):
    value: int  # type annotation only: all values should be int

    BOX_DOT_COM = 1001

    if __debug__:
        BLARG = -7


###
# helpers for accessing KnownAddonImps


def get_imp_by_name(imp_name: str) -> type[AddonImp]:
    return KnownAddonImps[imp_name].value


def get_imp_name(imp: type[AddonImp]) -> str:
    return KnownAddonImps(imp).name


def get_imp_by_number(imp_number: int) -> type[AddonImp]:
    _imp_name = AddonImpNumbers(imp_number).name
    return get_imp_by_name(_imp_name)


def get_imp_number(imp: type[AddonImp]) -> int:
    _imp_name = get_imp_name(imp)
    return AddonImpNumbers[_imp_name].value
