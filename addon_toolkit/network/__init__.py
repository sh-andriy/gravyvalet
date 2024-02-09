"""TODO: give addon implementers an easy way to declare the network requests
their addon needs while allowing consistent handling in any given addon_service
implementation
"""
import http
import logging


_logger = logging.getLogger(__name__)


async def send_request(self, http_method: http.HTTPMethod, url: str, **kwargs):
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
