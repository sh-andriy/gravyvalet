import dataclasses
import enum
import inspect
import logging
from typing import (
    Callable,
    Iterator,
)

from .declarator import ClassDeclarator
from .operation import (
    AddonOperationDeclaration,
    operation_declarator,
)


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
    # private methods for populating operations

    def __post_init__(self):
        self._gather_operations()

    def _gather_operations(self):
        for _name, _fn in inspect.getmembers(self.interface_cls, inspect.isfunction):
            _maybe_op = operation_declarator.get_declaration(_fn)
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


# the class decorator itself
addon_interface = ClassDeclarator(
    dataclass=AddonInterfaceDeclaration,
    target_fieldname="interface_cls",
)


@dataclasses.dataclass(frozen=True)
class AddonOperationImplementation:
    """dataclass for an implemented operation on an interface subclass"""

    implementation_cls: type
    operation: AddonOperationDeclaration

    def __post_init__(self):
        if self.implementation_fn is self.interface_fn:  # may raise NotImplementedError
            raise NotImplementedError(  # TODO: helpful exception type
                f"operation '{self.operation}' not implemented by {self.implementation_cls}"
            )

    @property
    def interface(self) -> AddonInterfaceDeclaration:
        return addon_interface.get_declaration_for_class(self.implementation_cls)

    @property
    def interface_fn(self) -> Callable:
        return getattr(self.interface.interface_cls, self.method_name)

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
    _interface_dec = addon_interface.get_declaration_for_class_or_instance(interface)
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
