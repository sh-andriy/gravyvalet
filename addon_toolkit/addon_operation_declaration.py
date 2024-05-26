import dataclasses
import enum
import inspect
from typing import (
    Callable,
    Iterator,
)

from . import exceptions
from .addon_operation_results import RedirectResult
from .capabilities import AddonCapabilities
from .declarator import Declarator


__all__ = (
    "AddonOperationDeclaration",
    "AddonOperationType",
    "addon_operation",
    "eventual_operation",
    "immediate_operation",
    "redirect_operation",
)


class AddonOperationType(enum.Enum):
    REDIRECT = "redirect"  # gravyvalet refers you somewhere helpful
    IMMEDIATE = "immediate"  # gravyvalet does a simple act, waiting to respond until done (success or problem)
    EVENTUAL = "eventual"  # gravyvalet starts a potentially long-running act, responding immediately with status


@dataclasses.dataclass(frozen=True)
class AddonOperationDeclaration:
    """dataclass for a declared operation method on an interface

    created by decorating a method with one of the "operation" decorators:
    `@redirect_operation`, `@immediate_operation`, `@eventual_operation`
    """

    operation_type: AddonOperationType
    capability: AddonCapabilities
    operation_fn: Callable  # the decorated function
    return_type: type = dataclasses.field(
        default=type(None),  # if not provided, inferred by __post_init__
        compare=False,
    )

    @classmethod
    def for_function(self, fn: Callable) -> "AddonOperationDeclaration":
        try:
            return addon_operation.get_declaration(fn)
        except ValueError:
            raise exceptions.NotAnOperation(fn)

    def __post_init__(self):
        if len(self.capability) != 1:
            raise exceptions.OperationNotValid
        _return_type = self.call_signature.return_annotation
        if self.return_type is type(None):
            # no return_type declared; infer from type annotation
            assert dataclasses.is_dataclass(
                _return_type
            ), f"operation methods must return a dataclass (got {_return_type} on {self.operation_fn})"
            # use object.__setattr__ to bypass dataclass frozenness (only here in __post_init__)
            object.__setattr__(self, "return_type", _return_type)
        else:
            # return_type declared; enforce it
            assert dataclasses.is_dataclass(
                self.return_type
            ), f"return_type must be a dataclass (got {self.return_type})"
            if not issubclass(_return_type, self.return_type):
                raise exceptions.OperationNotValid(
                    f"expected return type {self.return_type} on operation function {self.operation_fn} (got {_return_type})"
                )

    @property
    def name(self):
        # TODO: language tag (kwarg for tagged string?)
        return self.operation_fn.__name__

    @property
    def docstring(self) -> str:
        # TODO: language tag
        # TODO: docstring/description param on operation decorators, since __doc__ is removed on -O
        return self.operation_fn.__doc__ or ""

    @property
    def call_signature(self) -> inspect.Signature:
        return inspect.signature(self.operation_fn)

    def param_dataclasses(self) -> Iterator[type]:
        for _param_name, _param in self.call_signature.parameters.items():
            if not dataclasses.is_dataclass(_param.annotation):
                raise exceptions.OperationNotValid(
                    f"operation parameters must have dataclass annotations (TODO: decorator to infer dataclass from annotated kwargs), got `{_param_name}: {_param.annotation}`"
                )
            yield _param.annotation


# declarator for all types of operations -- use operation_type-specific decorators below
addon_operation = Declarator(
    declaration_dataclass=AddonOperationDeclaration,
    field_for_target="operation_fn",
)

# decorator for operations that may be performed by a client request (e.g. redirect to waterbutler)
redirect_operation = addon_operation.with_kwargs(
    operation_type=AddonOperationType.REDIRECT,
    return_type=RedirectResult,
    # TODO: consider adding `save_invocation: bool = True`, set False here
)

# decorator for operations that must be performed by the server but should take only
# a short time, so a server may wait on the operation before responding to a request
# (e.g. get a metadata description of an item, list items in a given folder)
immediate_operation = addon_operation.with_kwargs(
    operation_type=AddonOperationType.IMMEDIATE,
)

# decorator for operations that must be performed by the server and may take a long time
# (e.g. move/copy file, archive file-tree, execute computation)
eventual_operation = addon_operation.with_kwargs(
    operation_type=AddonOperationType.EVENTUAL,
)