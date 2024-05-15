import inspect
import typing

from addon_toolkit import exceptions
from addon_toolkit.addon_operation_declaration import AddonOperationDeclaration


class AddonInterface:

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
        return AddonOperationDeclaration.for_function(getattr(cls, operation_name))
