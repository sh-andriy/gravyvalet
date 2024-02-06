import dataclasses
import inspect
import weakref
from typing import Callable

from addon_toolkit.base_addon_interface import BaseAddonInterface


__all__ = (
    "AddonOperation",
    "redirect_operation",
    "proxy_operation",
)


@dataclasses.dataclass
class AddonOperation:
    operation_iri: str
    interface_cls: type[BaseAddonInterface]
    interface_method_name: str


class _DecoratedOperation:
    """a wrapper object for decorated operation methods"""

    def __init__(self, operation_fn: Callable):
        self.operation_fn = operation_fn

    def __call__(self, *args, **kwargs):
        return self.operation_fn(*args, **kwargs)

    def __set_name__(self, cls, name):
        # register the operation (the whole point of _DecoratedOperation)
        # TODO: reconsider
        self.__get_interface_operations(cls).add(name)

    @classmethod
    def __get_operation_registry(cls):
        try:
            return cls.__operation_registry
        except AttributeError:
            _new_registry = cls.__operation_registry = weakref.WeakKeyDictionary()
            return _new_registry

    @classmethod
    def __get_interface_operations(cls, interface_cls):
        _operation_registry = cls.__get_operation_registry()
        try:
            return _operation_registry[interface_cls]
        except KeyError:
            _interface_operations = _operation_registry[interface_cls] = set()
            return _interface_operations

    @classmethod
    def __add_interface_operation(
        cls,
        interface_cls,
    ):
        _operation_registry = cls.__get_operation_registry()
        try:
            return _operation_registry[interface_cls]
        except KeyError:
            _interface_operations = _operation_registry[interface_cls] = set()
            return _interface_operations


def redirect_operation(fn: Callable) -> _DecoratedOperation:
    # decorator for operations that may be performed by a client request
    # (e.g. redirect to waterbutler)
    assert inspect.isfunction(fn)  # TODO: inspect function params
    assert not inspect.isawaitable(fn)
    # TODO: helpful error messaging for implementers
    return _DecoratedOperation(fn)


def proxy_operation(fn):
    # decorator for operations that require fetching data from elsewhere,
    # but make no changes (e.g. get a metadata description of an item,
    # list items in a given folder)
    assert inspect.isasyncgenfunction(fn)  # generate rdf triples?
    # TODO: assert based on `inspect.signature(fn).parameters`
    # TODO: assert based on return value?
    return _DecoratedOperation(fn)
