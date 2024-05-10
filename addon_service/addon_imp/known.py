"""the single static source of truth for addon implementations known to the addon service

import and add new implementations here to make them available in the api
"""

import enum

from addon_imps.storage import box_dot_com
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

    BOX_DOT_COM = box_dot_com.BoxDotComStorageImp

    if __debug__:
        BLARG = my_blarg.MyBlargStorage


###
# helpers for accessing KnownAddonImps


def get_imp_by_name(imp_name: str) -> type[AddonImp]:
    return KnownAddonImps[imp_name].value


def get_imp_name(imp: AddonImp) -> str:
    return KnownAddonImps(imp).name


def get_imp_by_number(imp_number: int) -> type[AddonImp]:
    for _enum_imp in KnownAddonImps:
        if _enum_imp.value.imp_number == imp_number:
            return _enum_imp.value
    raise KeyError


if __debug__:
    from collections import Counter

    _repeated_imp_numbers = [
        _imp_number
        for (_imp_number, _count) in Counter(
            _imp_enum.value.imp_number for _imp_enum in KnownAddonImps
        ).items()
        if _count > 1
    ]
    assert not _repeated_imp_numbers, f"repeated imp numbers!? {_repeated_imp_numbers}"
