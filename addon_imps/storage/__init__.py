import functools

from . import box_dot_com
from addon_toolkit import AddonImp
from addon_toolkit.storage import StorageAddonProtocol

StorageImp = functools.partial(AddonImp, addon_protocol_cls=StorageAddonProtocol)

BoxDotComImp = StorageImp(imp_cls=box_dot_com.BoxDotComStorageImp)

__all__ = (
    "box_dot_com",
    "BoxDotComImp",
    "StorageImp",
)
