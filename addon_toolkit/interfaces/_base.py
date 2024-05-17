import inspect
import typing

from addon_toolkit import exceptions
from addon_toolkit.addon_operation_declaration import AddonOperationDeclaration


class AddonInterface(typing.Protocol):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError(
            f"cannot instantiate {cls}! is only for declaring an interface"
        )

    ###
    # class methods

    @classmethod
    def iter_declared_operations(cls) -> typing.Iterator[AddonOperationDeclaration]:
        for _name, _fn in inspect.getmembers(cls, inspect.isfunction):
            try:
                yield AddonOperationDeclaration.for_function(_fn)
            except exceptions.NotAnOperation:
                continue

    @classmethod
    def get_operation_by_name(cls, operation_name: str) -> AddonOperationDeclaration:
        try:
            _operation_fn = getattr(cls, operation_name)
        except AttributeError:
            raise exceptions.NotAnOperation(cls, operation_name)
        return AddonOperationDeclaration.for_function(_operation_fn)
