import dataclasses
import enum
import inspect
import weakref
from typing import (
    Callable,
    ClassVar,
    Iterator,
)

from .interface import AddonInterface


__all__ = (
    "AddonOperation",
    "AddonOperationType",
    "proxy_operation",
    "redirect_operation",
)


class AddonOperationType(enum.Enum):
    REDIRECT = enum.auto()
    PROXY = enum.auto()


@dataclasses.dataclass
class _InterfaceOperations:
    by_capability: dict[enum.Enum, set["AddonOperation"]] = dataclasses.field(
        default_factory=dict,
    )
    by_method_name: dict[str, "AddonOperation"] = dataclasses.field(
        default_factory=dict,
    )

    def add_operation(self, operation: "AddonOperation"):
        assert operation.method_name not in self.by_method_name, (
            f"duplicate operation '{operation.method_name}'"
            f" on {operation.declaration_cls}"
        )
        self.by_method_name[operation.method_name] = operation
        self.by_capability.setdefault(
            operation.capability,
            set(),
        ).add(operation)


@dataclasses.dataclass(frozen=True)
class _UnboundAddonOperation:
    operation_fn: Callable
    operation_type: AddonOperationType
    capability: enum.Enum

    def __set_name__(self, cls, name):
        AddonOperation._register_operation(self, cls, name)
        # replace this _UnboundAddonOperation with the original function
        setattr(cls, name, self.operation_fn)


@dataclasses.dataclass(frozen=True)
class AddonOperation:
    operation_type: AddonOperationType
    capability: enum.Enum
    declaration_cls: type[AddonInterface]
    method_name: str

    # private registry for all decorated operations
    _registry: ClassVar[
        weakref.WeakKeyDictionary[
            type[AddonInterface],
            _InterfaceOperations,
        ]
    ] = weakref.WeakKeyDictionary()

    ###
    # methods for _registry interaction

    @classmethod
    def _register_operation(
        cls,
        unbound_operation: _UnboundAddonOperation,
        declaration_cls: type,
        method_name: str,
    ):
        _operation = cls(
            operation_type=unbound_operation.operation_type,
            capability=unbound_operation.capability,
            declaration_cls=declaration_cls,
            method_name=method_name,
        )
        try:
            _interface_ops = cls._registry[_operation.declaration_cls]
        except KeyError:
            _interface_ops = cls._registry[
                _operation.declaration_cls
            ] = _InterfaceOperations()
        _interface_ops.add_operation(_operation)

    @classmethod
    def operations_declared_on_interface(
        cls,
        interface_cls: type[AddonInterface],
        capability: enum.Enum | None = None,
    ) -> Iterator["AddonOperation"]:
        try:
            _interface_ops = cls._registry[interface_cls]
        except KeyError:
            return  # zero
        else:
            if capability is None:
                yield from _interface_ops.by_method_name.values()
            else:
                yield from _interface_ops.by_capability.get(capability, ())

    ###
    # instance methods

    def __post_init__(self):
        assert self.declaration_cls is not AddonInterface
        assert issubclass(self.declaration_cls, AddonInterface)

    def get_operation_method(
        self, interface: AddonInterface | type[AddonInterface]
    ) -> Callable:
        _interface_cls = interface if isinstance(interface, type) else type(interface)
        assert _interface_cls is not self.declaration_cls
        assert issubclass(_interface_cls, self.declaration_cls)
        _declared_fn = getattr(self.declaration_cls, self.method_name)
        _implemented_fn = getattr(_interface_cls, self.method_name)
        if _implemented_fn is _declared_fn:
            raise NotImplementedError(  # TODO: specific exception class
                f"operation '{self.method_name}' not implemented by {type(interface)}"
            )
        # now get the method directly on the arg (instead of _interface_cls)
        # to ensure a bound method when that arg is an interface instance
        return getattr(interface, self.method_name)

    def is_implemented_on(self, interface):
        try:
            return bool(self.get_operation_method(interface))
        except NotImplementedError:
            return False

    def invoke(self, interface, /, args=None, kwargs=None):
        # TODO: reconsider
        _op_method = self.get_operation_method(interface)
        return _op_method(*(args or ()), **(kwargs or {}))


def redirect_operation(capability: enum.Enum):
    def _redirect_operation_decorator(fn: Callable) -> _UnboundAddonOperation:
        # decorator for operations that may be performed by a client request
        # (e.g. redirect to waterbutler)
        assert inspect.isfunction(fn)  # TODO: inspect function params
        assert not inspect.isawaitable(fn)
        # TODO: helpful error messaging for implementers
        return _UnboundAddonOperation(fn, AddonOperationType.REDIRECT, capability)

    return _redirect_operation_decorator


def proxy_operation(capability: enum.Enum):
    def _proxy_operation_decorator(fn: Callable) -> _UnboundAddonOperation:
        # decorator for operations that require fetching data from elsewhere,
        # but make no changes (e.g. get a metadata description of an item,
        # list items in a given folder)
        # TODO: assert inspect.isasyncgenfunction(fn)  # generate rdf triples?
        # TODO: assert based on `inspect.signature(fn).parameters`
        # TODO: assert based on return value?
        return _UnboundAddonOperation(fn, AddonOperationType.PROXY, capability)

    return _proxy_operation_decorator
