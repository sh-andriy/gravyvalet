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
    "get_operation_declarations",
    "get_operation_implementations",
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
    capability_enum: type[enum.Enum]
    method_name_by_op: dict[AddonOperationDeclaration, str] = dataclasses.field(
        default_factory=dict,
    )
    ops_by_capability: dict[
        enum.Enum, set[AddonOperationDeclaration]
    ] = dataclasses.field(
        default_factory=dict,
    )

    ###
    # AddonInterfaceDeclaration stores references to declared interface classes

    # private storage linking a class to data gleaned from its decorator
    __declarations_by_cls: ClassVar[
        weakref.WeakKeyDictionary[type, "AddonInterfaceDeclaration"]
    ] = weakref.WeakKeyDictionary()

    @classmethod
    def declare(cls, capability_enum: type[enum.Enum]):
        def _cls_decorator(interface_cls: type) -> type:
            cls.__declarations_by_cls[interface_cls] = AddonInterfaceDeclaration(
                interface_cls, capability_enum
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
            _maybe_op = AddonOperationDeclaration.get_for_function(_fn)
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


@dataclasses.dataclass(frozen=True)
class AddonOperationImplementation:
    """dataclass for an implemented operation on an interface subclass"""

    implementation_cls: type
    operation: AddonOperationDeclaration

    def __post_init__(self):
        _interface_cls_fn = getattr(self.interface.interface_cls, self.method_name)
        if self.implementation_fn is _interface_cls_fn:
            raise NotImplementedError(  # TODO: helpful exception type
                f"operation '{self.operation}' not implemented by {self.implementation_cls}"
            )

    @property
    def interface(self) -> AddonInterfaceDeclaration:
        return AddonInterfaceDeclaration.for_class(self.implementation_cls)

    @property
    def method_name(self) -> str:
        return self.interface.method_name_by_op[self.operation]

    @property
    def implementation_fn(self) -> Callable:
        return getattr(self.implementation_cls, self.method_name)

    @property
    def combined_docstring(self) -> str | None:
        return "\n".join(
            (
                self.operation.docstring or "",
                self.implementation_fn.__doc__ or "",
            )
        )

    def get_callable_for(self, addon_instance: object) -> Callable:
        return getattr(addon_instance, self.method_name)


def get_operation_declarations(
    interface: type | object, capability: enum.Enum | None = None
) -> Iterator[AddonOperationDeclaration]:
    _interface_dec = AddonInterfaceDeclaration.for_class_or_instance(interface)
    if capability is None:
        yield from _interface_dec.method_name_by_op.keys()
    else:
        yield from _interface_dec.ops_by_capability.get(capability, ())


def get_operation_implementations(
    implementation_cls: type,
    capability: enum.Enum | None = None,
) -> Iterator[AddonOperationImplementation]:
    for _op in get_operation_declarations(implementation_cls, capability=capability):
        try:
            yield AddonOperationImplementation(implementation_cls, _op)
        except NotImplementedError:
            pass


def is_operation_implemented_on(
    operation: AddonOperationDeclaration,
    implementation_cls: type,
) -> bool:
    try:
        return bool(AddonOperationImplementation(implementation_cls, operation))
    except NotImplementedError:  # TODO: more specific error
        return False


def invoke(
    operation: AddonOperationDeclaration,
    interface_instance: object,
    /,
    args=None,
    kwargs=None,
):
    # TODO: reconsider
    _imp = AddonOperationImplementation(interface_instance.__class__, operation)
    _method = _imp.get_callable_for(interface_instance)
    return _method(*(args or ()), **(kwargs or {}))
