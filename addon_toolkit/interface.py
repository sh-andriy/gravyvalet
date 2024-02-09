import dataclasses
import enum
import inspect
import logging
import weakref
from typing import (
    Callable,
    ClassVar,
    Iterator,
    Optional,
)

from .operation import AddonOperationDeclaration


__all__ = ("addon_interface", "PagedResult")

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

    @staticmethod
    def declare(capabilities: type[enum.Enum]):
        def _cls_decorator(interface_cls: type) -> type:
            AddonInterfaceDeclaration.__declarations_by_cls[
                interface_cls
            ] = AddonInterfaceDeclaration(interface_cls, capabilities)
            return interface_cls

        return _cls_decorator

    @staticmethod
    def for_class(interface_cls: type) -> Optional["AddonInterfaceDeclaration"]:
        return AddonInterfaceDeclaration.__declarations_by_cls.get(interface_cls)

    ###
    # AddonInterfaceDeclaration instance methods

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

    def get_operation_method(
        self, cls_or_instance: type | object, operation: AddonOperationDeclaration
    ) -> Callable:
        _cls = (
            cls_or_instance
            if isinstance(cls_or_instance, type)
            else type(cls_or_instance)
        )
        assert self.interface_cls is not _cls
        assert issubclass(_cls, self.interface_cls)
        try:
            _method_name = self.method_name_by_op[operation]
        except KeyError:
            raise ValueError  # TODO: helpful exception type
        _declared_fn = getattr(self.interface_cls, _method_name)
        _implemented_fn = getattr(_cls, _method_name)
        if _implemented_fn is _declared_fn:
            raise NotImplementedError(  # TODO: helpful exception type
                f"operation '{_method_name}' not implemented by {_cls}"
            )
        # now get the method directly on what was passed in
        # to ensure a bound method when that arg is an interface instance
        return getattr(cls_or_instance, _method_name)

    def operation_is_implemented(
        self, implementation_cls: type, operation: AddonOperationDeclaration
    ):
        try:
            return bool(self.get_operation_method(implementation_cls, operation))
        except NotImplementedError:  # TODO: more specific error
            return False

    def invoke(self, operation, interface_instance, /, args=None, kwargs=None):
        # TODO: reconsider
        _op_method = self.get_operation_method(interface_instance, operation)
        return _op_method(*(args or ()), **(kwargs or {}))

    def get_declared_operations(
        self,
        *,
        capability: enum.Enum | None = None,
    ) -> Iterator[AddonOperationDeclaration]:
        if capability is None:
            yield from self.method_name_by_op.keys()
        else:
            yield from self.ops_by_capability.get(capability, ())

    def get_implemented_operations(
        self,
        implementation_cls: type,
        capability: enum.Enum | None = None,
    ) -> Iterator[AddonOperationDeclaration]:
        for _op in self.get_declared_operations(capability=capability):
            if self.operation_is_implemented(implementation_cls, _op):
                yield _op


# meant for use as decorator on a class, `@addon_interface(MyCapabilitiesEnum)`
addon_interface = AddonInterfaceDeclaration.declare
