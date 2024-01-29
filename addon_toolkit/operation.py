import dataclasses
import inspect
import logging
from typing import Callable

from addon_toolkit.namespaces import GRAVY


__all__ = (  # public module attrs:
    "immediate_operation",
    "proxy_read_operation",
    "proxy_act_operation",
)

_logger = logging.getLogger(__name__)


###
# decorators to declare operations on interface classes


def immediate_operation(fn):
    # decorator for operations that can be computed immediately,
    # without sending any requests or waiting on external resources
    # (e.g. build a url in a known pattern or return declared static metadata)
    assert inspect.isfunction(fn)
    assert not inspect.isawaitable(fn)
    # TODO: assert based on `inspect.signature(fn).parameters`
    # TODO: helpful error messaging for implementers
    return _DecoratedOperation(fn)


def proxy_read_operation(fn):
    # decorator for operations that require fetching data from elsewhere,
    # but make no changes (e.g. get a metadata description of an item,
    # list items in a given folder)
    assert inspect.isasyncgenfunction(fn)
    # TODO: assert based on `inspect.signature(fn).parameters`
    # TODO: assert based on return value?
    return _DecoratedOperation(fn)


def proxy_act_operation(fn):
    # decorator for operations that initiate change, may take some time,
    # and may fail in strange ways (e.g. delete an item, copy a file tree)
    assert inspect.iscoroutine(fn)
    # TODO: assert based on `inspect.signature(fn).parameters`
    # TODO: assert based on return value?
    return _DecoratedOperation(fn)


###
# module-private helpers


@dataclasses.dataclass
class _DecoratedOperation:
    """a temporary object for decorated operation methods"""

    operation_fn: Callable

    def __set_name__(self, cls, name):
        # called for each decorated class method
        _operation_method_map = _get_operation_method_map(cls)
        assert name not in _operation_method_map
        _operation_method_map[name]
        # overwrite this _DecoratedOperation with the operation_fn
        # now that operation record-keeping has completed
        setattr(cls, name, self.operation_fn)


def _get_operation_iri(fn):
    # may raise AttributeError
    return getattr(fn, GRAVY.operation)


def _set_operation_iri(operation_fn, operation_iri):
    try:
        _prior_value = _get_operation_iri(operation_fn)
    except AttributeError:
        _prior_value = None
    if _prior_value is not None:
        raise ValueError("cannot call _set_operation_iri twice (on %r)", operation_fn)
    setattr(operation_fn, GRAVY.operation, operation_iri)


def _get_operation_method_map(obj):
    try:
        return getattr(obj, GRAVY.operation_map)
    except AttributeError:
        _operation_method_map = {}
        setattr(obj, GRAVY.operation_map, _operation_method_map)
        return _operation_method_map
