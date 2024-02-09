from .interface import (
    PagedResult,
    addon_interface,
    get_declared_operations,
    get_implemented_operations,
    get_operation_fn_on,
    is_operation_implemented_on,
)
from .operation import (
    proxy_operation,
    redirect_operation,
)


__all__ = (
    "PagedResult",
    "addon_interface",
    "proxy_operation",
    "redirect_operation",
    "get_declared_operations",
    "get_implemented_operations",
    "get_operation_fn_on",
    "is_operation_implemented_on",
)
