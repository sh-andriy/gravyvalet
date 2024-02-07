import dataclasses
import logging
from http import HTTPMethod


__all__ = ("AddonInterface", "PagedResult")


_logger = logging.getLogger(__name__)


###
# addon interface


@dataclasses.dataclass
class PagedResult:  # TODO: consistent handling of paged results
    page: list
    next_page_cursor: str


@dataclasses.dataclass
class AddonInterface:
    ###
    # public api for use on `self` when implementing operations

    # TODO: consider intermediate dataclasses to limit direct use of data models
    # authorized_account: AuthorizedStorageAccount
    # configured_addon: ConfiguredStorageAddon | None

    async def send_request(self, http_method: HTTPMethod, url: str, **kwargs):
        """helper for external requests in addon implementations

        subclasses SHOULD use this instead of sending requests by hand
        """
        _logger.info("sending %s to %s", http_method, url)
        # TODO: common http handling (retry, backoff, etc) to ease implementer load
        # async with httpx.AsyncClient() as _client:  # TODO: shared client?
        #     _response = await _client.request(
        #         http_method,
        #         url,
        #         **kwargs,
        #     )
        #     return _response
