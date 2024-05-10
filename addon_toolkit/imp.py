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
from .interfaces import AddonInterfaces  # TODO: resolve circular import
from .json_arguments import kwargs_from_json


__all__ = (
    "AddonImp",
    "AddonOperationImp",
)


class AddonImp:
    """base class for all addon implementations"""

    def __init__(self, *args, **kwargs):
        _cls = type(self)
        if (_cls is AddonImp) or (_cls in AddonInterfaces):
            raise exceptions.ImpNotInstantiatable(_cls)

    @classmethod
    def get_interface_cls(cls) -> type["AddonImp"]:
        return AddonInterfaces.get_for_imp_cls(cls).value

    @classmethod
    def get_operation_declarations(
        cls,
        *,
        capabilities: AddonCapabilities | None = None,
    ) -> typing.Iterator[AddonOperationDeclaration]:
        _interface_cls = AddonInterfaces.get_for_imp_cls(cls).value
        for _name, _fn in inspect.getmembers(_interface_cls, inspect.isfunction):
            try:
                _op = AddonOperationDeclaration.for_function(_fn)
            except exceptions.NotAnOperation:
                continue
            if (not capabilities) or (_op.capability in capabilities):
                yield _op

    @classmethod
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
                yield AddonOperationImp(addon_imp_cls=cls, declaration=_declaration)
            except exceptions.OperationNotImplemented:
                pass  # operation not implemented

    @classmethod
    def get_operation_imp_by_name(cls, operation_name: str) -> "AddonOperationImp":
        # may raise OperationNotImplemented
        return AddonOperationImp(
            addon_imp_cls=cls,
            declaration=cls.get_operation_declaration_by_name(operation_name),
        )


@dataclasses.dataclass(frozen=True)
class AddonOperationImp:
    """dataclass for an operation implemented by a concrete AddonImp subclass"""

    addon_imp_cls: type[AddonImp]
    declaration: AddonOperationDeclaration

    def __post_init__(self) -> None:
        if self.interface_function is self.imp_function:
            raise exceptions.OperationNotImplemented(self)

    @functools.cached_property
    def interface_function(self):
        try:
            return getattr(
                self.addon_imp_cls.get_interface_cls(),
                self.declaration.name,
            )
        except AttributeError:
            raise exceptions.OperationNotValid(self)

    @functools.cached_property
    def imp_function(self):
        try:
            return getattr(self.addon_imp_cls, self.declaration.name)
        except AttributeError:
            raise exceptions.OperationNotValid(self)

    async def invoke_thru_addon(self, addon_instance: object, json_kwargs: dict):
        _method = self._get_instance_method(addon_instance)
        _kwargs = kwargs_from_json(self.declaration.call_signature, json_kwargs)
        if not inspect.iscoroutinefunction(_method):
            _method = sync_to_async(_method)
        _result = await _method(**_kwargs)
        assert isinstance(_result, self.declaration.return_type)
        return _result

    invoke_thru_addon__blocking = async_to_sync(invoke_thru_addon)

    def _get_instance_method(self, addon_instance: object):
        return getattr(addon_instance, self.declaration.name)

    # TODO: async def async_call_with_json_kwargs(self, addon_instance: object, json_kwargs: dict):
