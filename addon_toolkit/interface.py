import dataclasses
import enum
import inspect
import logging
import weakref
from typing import (
    Callable,
    ClassVar,
    Iterator,
)

from .operation import AddonOperationDeclaration


__all__ = (
    "PagedResult",
    "addon_interface",
    "get_declared_operations",
    "get_implemented_operations",
    "get_operation_fn_on",
    "is_operation_implemented_on",
)

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PagedResult:  # TODO: consistent handling of paged results
    page: list
    next_page_cursor: str


@dataclasses.dataclass
class AddonInterfaceDeclaration:
    """dataclass for the operations declared on a class decorated with `addon_interface`"""

    interface_cls: type
    capabilities: type[enum.Enum]
    method_name_by_op: dict[AddonOperationDeclaration, str] = dataclasses.field(
        default_factory=dict,
    )
    ops_by_capability: dict[
        enum.Enum, set[AddonOperationDeclaration]
    ] = dataclasses.field(
        default_factory=dict,
    )

    ###
    # AddonInterface stores references to declared interface classes

    # private storage linking a class to data gleaned from its decorator
    __declarations_by_cls: ClassVar[
        weakref.WeakKeyDictionary[type, "AddonInterfaceDeclaration"]
    ] = weakref.WeakKeyDictionary()

    @classmethod
    def declare(cls, capabilities: type[enum.Enum]):
        def _cls_decorator(interface_cls: type) -> type:
            cls.__declarations_by_cls[interface_cls] = AddonInterfaceDeclaration(
                interface_cls, capabilities
            )
            return interface_cls

        return _cls_decorator

    @classmethod
    def for_class_or_instance(
        cls, interface: type | object
    ) -> "AddonInterfaceDeclaration":
        _interface_cls = interface if isinstance(interface, type) else type(interface)
        return cls.for_class(_interface_cls)

    @classmethod
    def for_class(cls, interface_cls: type) -> "AddonInterfaceDeclaration":
        for _cls in interface_cls.__mro__:
            try:
                return AddonInterfaceDeclaration.__declarations_by_cls[_cls]
            except KeyError:
                pass
        raise ValueError(f"no addon_interface declaration found for {interface_cls}")

    ###
    # private methods for populating operations

    def __post_init__(self):
        self._gather_operations()

    def _gather_operations(self):
        for _name, _fn in inspect.getmembers(self.interface_cls, inspect.isfunction):
            _maybe_op = AddonOperationDeclaration.for_function(_fn)
            if _maybe_op is not None:
                self._add_operation(_name, _maybe_op)

    def _add_operation(self, method_name: str, operation: AddonOperationDeclaration):
        assert operation not in self.method_name_by_op, (
            f"duplicate operation '{operation}'" f" on {self.interface_cls}"
        )
        self.method_name_by_op[operation] = method_name
        self.ops_by_capability.setdefault(
            operation.capability,
            set(),
        ).add(operation)


# meant for use as decorator on a class, `@addon_interface(MyCapabilitiesEnum)`
addon_interface = AddonInterfaceDeclaration.declare


def get_declared_operations(
    interface: type | object, capability: enum.Enum | None = None
) -> Iterator[AddonOperationDeclaration]:
    _interface_dec = AddonInterfaceDeclaration.for_class_or_instance(interface)
    if capability is None:
        yield from _interface_dec.method_name_by_op.keys()
    else:
        yield from _interface_dec.ops_by_capability.get(capability, ())


def get_implemented_operations(
    interface: type | object,
    capability: enum.Enum | None = None,
) -> Iterator[AddonOperationDeclaration]:
    for _op in get_declared_operations(interface, capability=capability):
        if is_operation_implemented_on(_op, interface):
            yield _op


def get_operation_fn_on(
    operation: AddonOperationDeclaration,
    interface: type | object,
) -> Callable:
    _interface_cls = interface if isinstance(interface, type) else type(interface)
    _interface_dec = AddonInterfaceDeclaration.for_class(_interface_cls)
    try:
        _method_name = _interface_dec.method_name_by_op[operation]
    except KeyError:
        raise ValueError  # TODO: helpful exception type
    _declared_fn = getattr(_interface_dec.interface_cls, _method_name)
    _implemented_fn = getattr(_interface_cls, _method_name)
    if _implemented_fn is _declared_fn:
        raise NotImplementedError(  # TODO: helpful exception type
            f"operation '{_method_name}' not implemented by {_interface_cls}"
        )
    # now get the method directly on what was passed in
    # to ensure a bound method when that arg is an interface instance
    return getattr(interface, _method_name)


def is_operation_implemented_on(
    operation: AddonOperationDeclaration,
    interface: type | object,
) -> bool:
    try:
        return bool(get_operation_fn_on(operation, interface))
    except NotImplementedError:  # TODO: more specific error
        return False


def invoke(operation, interface_instance, /, args=None, kwargs=None):
    # TODO: reconsider
    _op_method = get_operation_fn_on(operation, interface_instance)
    return _op_method(*(args or ()), **(kwargs or {}))
