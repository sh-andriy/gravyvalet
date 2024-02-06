import dataclasses
import inspect
import logging
from http import HTTPMethod
from typing import Callable

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
    def __get_declared_operations(cls) -> dict:
        assert cls is not BaseAddonInterface
        try:
            return cls.__declared_operations
        except AttributeError:
            _declared_operations = {}
            cls.__declared_operations = _declared_operations
            return _declared_operations

    @classmethod
    def _register_operation(cls, method_name, operation_fn):
        _operations = cls.__get_declared_operations()
        _operations[method_name] = operation_fn

    def __get_operation_method(self, operation_iri: str):
        _declared_operations = self.__declared_operations()
        try:
            _methodname, _fn = _declared_operations[operation_iri]
        except AttributeError:
            return NotImplemented
        # TODO: _method = getattr(...
