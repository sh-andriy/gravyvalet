import dataclasses
import inspect
import logging
from http import HTTPMethod

import httpx  # TODO: reconsider new dependency

from addon_service.models import (
    AuthorizedStorageAccount,
    ConfiguredStorageAddon,
)
from addon_service.operation import _get_operation_iri


__all__ = ("BaseAddonInterface",)


_logger = logging.getLogger(__name__)


###
# addon interface


@dataclasses.dataclass
class BaseAddonInterface:
    ###
    # public api for use on `self` when implementing operations

    # TODO: consider intermediate dataclasses to limit direct use of data models
    authorized_account: AuthorizedStorageAccount
    configured_addon: ConfiguredStorageAddon | None

    async def send_request(self, http_method: HTTPMethod, url: str, **kwargs):
        """helper for external requests in addon implementations

        subclasses SHOULD use this instead of sending requests by hand
        """
        # TODO: common http handling (retry, backoff, etc) to ease implementer load
        _logger.info("sending %s to %s", http_method, url)
        async with httpx.AsyncClient() as _client:  # TODO: shared client?
            _response = await _client.request(
                http_method,
                url,
                **kwargs,
            )
            return _response

    ###
    # private api for operation book-keeping

    @classmethod
    def __declared_operations(cls):
        try:
            return cls.__declared_operations
        except AttributeError:
            _declared_operations = cls.__declared_operations = dict(
                cls.__iter_declared_operations()
            )
            return _declared_operations

    @classmethod
    def __iter_declared_operations(cls):
        for _methodname, _fn in inspect.getmembers(cls, inspect.ismethod):
            try:
                _operation_iri = _get_operation_iri(_fn)
            except AttributeError:
                pass
            else:  # is operation
                yield (_operation_iri, (_methodname, _fn))

        raise NotImplementedError  # TODO

    def __get_operation_method(self, operation_iri: str):
        _declared_operations = self.__declared_operations()
        try:
            _methodname, _fn = _declared_operations[operation_iri]
        except AttributeError:
            return NotImplemented
        # TODO: _method = getattr(...


immediate_operation = BaseAddonInterface._immediate_operation
proxy_read_operation = BaseAddonInterface._proxy_read_operation
proxy_act_operation = BaseAddonInterface._proxy_act_operation
