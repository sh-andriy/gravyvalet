import dataclasses
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


__all__ = (
    "AddonImp",
    "AddonOperationImp",
)


class AddonImp:
    """base class for all addon implementations"""

    def __new__(cls):
        if cls is AddonImp:
            raise exceptions.ImpTooAbstract(cls)
        if not issubclass(cls, cls.get_interface_cls()):
            raise exceptions.BadImp(cls)
        return super().__new__(cls)

    @classmethod
    @functools.cache
    def get_interface_cls(cls) -> type["AddonImp"]:
        # circular import (TODO: consider reorganizing to avoid?)
        from .interfaces import AddonInterfaces

        return AddonInterfaces.for_concrete_imp(cls).value

    @classmethod
    def get_operation_declarations(
        cls,
        *,
        capabilities: AddonCapabilities | None = None,
    ) -> typing.Iterator[AddonOperationDeclaration]:
        for _name, _fn in inspect.getmembers(
            cls.get_interface_cls(), inspect.isfunction
        ):
            try:
                _op = AddonOperationDeclaration.for_function(_fn)
            except exceptions.NotAnOperation:
                continue
            if (not capabilities) or (_op.capability in capabilities):
                yield _op

    @classmethod
    @functools.cache
    def get_operation_declaration_by_name(
        cls, op_name: str
    ) -> AddonOperationDeclaration:
        return AddonOperationDeclaration.for_function(
            getattr(cls.get_interface_cls(), op_name),
        )

    @classmethod
    def get_operation_imps(
        cls, *, capabilities: AddonCapabilities | None = None
    ) -> typing.Iterator["AddonOperationImp"]:
        for _declaration in cls.get_operation_declarations(capabilities=capabilities):
            try:
                yield AddonOperationImp(addon_imp=cls, declaration=_declaration)
            except exceptions.OperationNotImplemented:
                pass  # operation not implemented

    @classmethod
    @functools.cache
    def get_operation_imp_by_name(cls, operation_name: str) -> "AddonOperationImp":
        # may raise OperationNotImplemented
        return AddonOperationImp(
            addon_imp=cls,
            declaration=cls.get_operation_declaration_by_name(operation_name),
        )

    async def invoke_operation(self, operation_name: str, json_kwargs: dict):
        _operation_imp = self.get_operation_imp_by_name(operation_name)
        _operation_declaration = _operation_imp.declaration
        _operation_method = getattr(self, _operation_declaration.name)
        if _operation_method.__func__ is not _operation_imp.imp_function:
            raise exceptions.OperationNotValid
        _kwargs = kwargs_from_json(_operation_declaration.call_signature, json_kwargs)
        if not inspect.iscoroutinefunction(_operation_method):
            _operation_method = sync_to_async(_operation_method)
        _result = await _operation_method(**_kwargs)
        assert isinstance(_result, _operation_declaration.return_type)
        return _result

    invoke_operation__blocking = async_to_sync(invoke_operation)


@dataclasses.dataclass(frozen=True)
class AddonOperationImp:
    """dataclass for an operation implemented by a concrete AddonImp subclass"""

    addon_imp: type[AddonImp]  # concrete subclass of AddonImp
    declaration: AddonOperationDeclaration

    def __post_init__(self) -> None:
        if self.interface_function is self.imp_function:
            raise exceptions.OperationNotImplemented(self)

    @functools.cached_property
    def interface_function(self):
        try:
            return getattr(
                self.addon_imp.get_interface_cls(),
                self.declaration.name,
            )
        except AttributeError:
            raise exceptions.OperationNotValid(self)

    @functools.cached_property
    def imp_function(self):
        try:
            return getattr(self.addon_imp, self.declaration.name)
        except AttributeError:
            raise exceptions.OperationNotValid(self)
