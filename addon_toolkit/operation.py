import dataclasses
import enum
from typing import Callable

from .declarator import Declarator


__all__ = (
    "AddonOperationDeclaration",
    "AddonOperationType",
    "operation_declarator",
    "proxy_operation",
    "redirect_operation",
)


class AddonOperationType(enum.Enum):
    REDIRECT = "redirect"
    PROXY = "proxy"


@dataclasses.dataclass(frozen=True)
class AddonOperationDeclaration:
    """dataclass for a declared operation method on an interface

    created by decorating a method with `@proxy_operation` or `@redirect_operation`
    on a class decorated with `@addon_operation`.
    """

    operation_type: AddonOperationType
    capability: enum.Enum
    operation_fn: Callable

    ###
    # instance methods

    @property
    def docstring(self) -> str | None:
        # TODO: consider docstring param on operation decorators, allow overriding __doc__
        return self.operation_fn.__doc__

    @classmethod
    def for_function(self, fn: Callable) -> "AddonOperationDeclaration":
        return operation_declarator.get_declaration(fn)


# decorator for operations (used by operation_type-specific decorators below)
operation_declarator = Declarator(
    declaration_dataclass=AddonOperationDeclaration,
    object_field="operation_fn",
)

# decorator for operations that may be performed by a client request (e.g. redirect to waterbutler)
redirect_operation = operation_declarator.with_kwargs(
    operation_type=AddonOperationType.REDIRECT,
)

# decorator for operations that require fetching data from elsewhere, but make no changes
# (e.g. get a metadata description of an item, list items in a given folder)
proxy_operation = operation_declarator.with_kwargs(
    operation_type=AddonOperationType.PROXY,
)
