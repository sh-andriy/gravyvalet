import dataclasses
import enum
import inspect
import weakref
from typing import (
    Callable,
    ClassVar,
    Optional,
)


__all__ = (
    "AddonOperationDeclaration",
    "AddonOperationType",
    "proxy_operation",
    "redirect_operation",
)


class AddonOperationType(enum.Enum):
    REDIRECT = "redirect"
    PROXY = "redirect"


@dataclasses.dataclass(frozen=True)
class AddonOperationDeclaration:
    """dataclass for a declared operation method on a subclass of AddonInterface

    created by the decorators "proxy_operation" and "redirect_operation"
    """

    operation_type: AddonOperationType
    capability: enum.Enum
    operation_fn: Callable

    ###
    # AddonOperationDeclaration stores references to declared operations

    # private storage linking a function to data gleaned from its decorator
    __operations_by_fn: ClassVar[
        weakref.WeakKeyDictionary[Callable, "AddonOperationDeclaration"]
    ] = weakref.WeakKeyDictionary()

    @staticmethod
    def declared(
        operation_fn: Callable,
        capability: enum.Enum,
        operation_type: AddonOperationType,
    ):
        AddonOperationDeclaration.__operations_by_fn[
            operation_fn
        ] = AddonOperationDeclaration(
            operation_type=operation_type,
            capability=capability,
            operation_fn=operation_fn,
        )

    @staticmethod
    def for_function(fn: Callable) -> Optional["AddonOperationDeclaration"]:
        return AddonOperationDeclaration.__operations_by_fn.get(fn)


def redirect_operation(capability: enum.Enum):
    def _redirect_operation_decorator(fn: Callable) -> Callable:
        # decorator for operations that may be performed by a client request
        # (e.g. redirect to waterbutler)
        assert inspect.isfunction(fn)  # TODO: inspect function params
        assert not inspect.isawaitable(fn)
        # TODO: helpful error messaging for implementers
        AddonOperationDeclaration.declared(fn, capability, AddonOperationType.REDIRECT)
        return fn

    return _redirect_operation_decorator


def proxy_operation(capability: enum.Enum):
    def _proxy_operation_decorator(fn: Callable) -> Callable:
        # decorator for operations that require fetching data from elsewhere,
        # but make no changes (e.g. get a metadata description of an item,
        # list items in a given folder)
        # TODO: assert inspect.isasyncgenfunction(fn)  # generate rdf triples?
        # TODO: assert based on `inspect.signature(fn).parameters`
        # TODO: assert based on return value?
        AddonOperationDeclaration.declared(fn, capability, AddonOperationType.PROXY)
        return fn

    return _proxy_operation_decorator
