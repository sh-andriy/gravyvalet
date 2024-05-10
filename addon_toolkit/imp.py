import functools
import inspect
import typing

from asgiref.sync import (
    async_to_sync,
    sync_to_async,
)

from . import exceptions
from .addon_operation_declaration import AddonOperationDeclaration
from .capabilities import AddonCapabilities
from .json_arguments import kwargs_from_json


__all__ = ("AddonImp",)


class AddonImp:
    """base class for all addon implementations"""

    def __new__(cls, *args, **kwargs):
        if cls is AddonImp:
            raise exceptions.ImpTooAbstract(cls)
        if not issubclass(cls, cls.get_interface_cls()):
            raise exceptions.ImpNotValid(cls)
        return super().__new__(cls)

    @classmethod
    @functools.cache
    def get_interface_cls(cls) -> type["AddonImp"]:
        # circular import (TODO: consider reorganizing to avoid?)
        from .interfaces import AddonInterfaces

        return AddonInterfaces.for_concrete_imp(cls).value

    @classmethod
    def iter_declared_operations(
        cls,
    ) -> typing.Iterator[AddonOperationDeclaration]:
        for _name, _fn in inspect.getmembers(
            cls.get_interface_cls(), inspect.isfunction
        ):
            try:
                yield AddonOperationDeclaration.for_function(_fn)
            except exceptions.NotAnOperation:
                continue

    @classmethod
    @functools.cache
    def get_operation_by_name(
        cls,
        operation_name: str,
        /,  # all args positional-only (for cache's sake)
    ) -> AddonOperationDeclaration:
        return AddonOperationDeclaration.for_function(
            getattr(cls.get_interface_cls(), operation_name),
        )

    @classmethod
    @functools.cache
    def all_implemented_operations(cls) -> frozenset[AddonOperationDeclaration]:
        return frozenset(
            _operation
            for _operation in cls.iter_declared_operations()
            if cls.has_implemented_operation(_operation)
        )

    @classmethod
    def implemented_operations_for_capabilities(
        cls, capabilities: AddonCapabilities
    ) -> typing.Iterator[AddonOperationDeclaration]:
        for _operation in cls.all_implemented_operations():
            if _operation.capability in capabilities:
                yield _operation

    @classmethod
    def has_implemented_operation(cls, operation: AddonOperationDeclaration):
        try:
            return bool(cls.get_imp_function(operation))
        except exceptions.OperationNotImplemented:
            return False

    @classmethod
    def get_interface_function(self, operation: AddonOperationDeclaration):
        try:
            return getattr(self.get_interface_cls(), operation.name)
        except AttributeError:
            raise exceptions.OperationNotValid(self, operation)

    @classmethod
    def get_imp_function(cls, operation: AddonOperationDeclaration):
        _imp_function = getattr(cls, operation.name, None)
        if _imp_function in (None, cls.get_interface_function(operation)):
            raise exceptions.OperationNotImplemented(cls, operation)
        return _imp_function

    ###
    # instance methods

    def get_imp_method(self, operation: AddonOperationDeclaration):
        _imp_method = getattr(self, operation.name)
        if _imp_method.__func__ is not self.get_imp_function(operation):
            raise exceptions.OperationNotValid(self, operation)
        return _imp_method

    async def invoke_operation(
        self, operation: AddonOperationDeclaration, json_kwargs: dict
    ):
        _operation_method = self.get_imp_method(operation)
        _kwargs = kwargs_from_json(operation.call_signature, json_kwargs)
        if not inspect.iscoroutinefunction(_operation_method):
            _operation_method = sync_to_async(_operation_method)
        _result = await _operation_method(**_kwargs)
        assert isinstance(_result, operation.return_type)
        return _result

    invoke_operation__blocking = async_to_sync(invoke_operation)
