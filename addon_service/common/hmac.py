import base64
import functools
import hashlib
import hmac
import re
import urllib.parse
from datetime import (
    UTC,
    datetime,
    timedelta,
)

from django.http import HttpRequest


__all__ = (
    "make_signed_headers",
    "get_signed_headers",
    "validate_signed_request",
    "TIMESTAMP_HEADER",
)

# this is but one way to hmac-sign an http request -- aligns with how osf sends them:
# https://github.com/CenterForOpenScience/osf.io/blob/develop/osf/external/gravy_valet/auth_helpers.py

_AUTH_HEADER_SCHEME = "HMAC-SHA256"
_AUTH_HEADER_REGEX = re.compile(
    "^"
    + re.escape(_AUTH_HEADER_SCHEME)
    + r" SignedHeaders=(?P<headers>[\w;-]*)&Signature=(?P<signature>[^\W_]*$)"
)
TIMESTAMP_HEADER = "X-Authorization-Timestamp"
CONTENT_HASH_HEADER = "X-Content-SHA256"


###
# public


def make_signed_headers(
    request_url: str,
    request_method: str,
    hmac_key: str,
    request_content: bytes = b"",
    additional_headers: dict[str, str] | None = None,
) -> dict:
    signed_string_segments, signed_headers = _get_signed_components(
        request_url, request_method, request_content, additional_headers
    )
    signature = _sign_message(
        message="\n".join(signed_string_segments), hmac_key=hmac_key
    )
    signature_header_fields = ";".join(signed_headers.keys())
    auth_header_value = f"{_AUTH_HEADER_SCHEME} SignedHeaders={signature_header_fields}&Signature={signature}"
    return dict(
        **signed_headers,
        Authorization=auth_header_value,
    )


@functools.lru_cache
def get_signed_headers(
    request: HttpRequest, hmac_key: str, expiration_seconds: int | None = None
) -> dict[str, str]:
    _authorization = request.headers.get("Authorization", "")
    if not _authorization.startswith(_AUTH_HEADER_SCHEME):
        raise NotUsingHmac
    match = _AUTH_HEADER_REGEX.match(_authorization)
    if not match:
        raise UnsupportedHmacAuthorization(
            "Message was not authorized via valid HMAC-SHA256 signed headers"
        )
    expected_signature = match.group("signature")
    signed_header_names = match.group("headers").split(";")
    signed_headers = {
        _header_name: str(request.headers[_header_name])
        for _header_name in signed_header_names
    }
    computed_signature = _sign_message(
        message=_reconstruct_string_to_sign_from_request(
            request, signed_headers=signed_headers
        ),
        hmac_key=hmac_key,
    )
    if not hmac.compare_digest(computed_signature, expected_signature):
        raise IncorrectHmacSignature("HMAC Signed Request has incorrect signature!")
    if expiration_seconds is not None:
        _validate_timestamp(signed_headers.get(TIMESTAMP_HEADER), expiration_seconds)
    content_hash = signed_headers.get(CONTENT_HASH_HEADER)
    if content_hash:
        _validate_content_hash(content_hash, request.body)
    return signed_headers


def validate_signed_request(
    request: HttpRequest, hmac_key: str, expiration_seconds: int | None = None
) -> None:
    # will raise error if invalid
    get_signed_headers(
        request=request, hmac_key=hmac_key, expiration_seconds=expiration_seconds
    )


###
# exceptions raised in this module


class NotUsingHmac(ValueError):
    pass


class RejectedHmac(ValueError):
    pass


class ExpiredHmacTimestamp(RejectedHmac):
    pass


class FutureHmacTimestamp(RejectedHmac):
    pass


class UnsupportedHmacAuthorization(RejectedHmac):
    pass


class IncorrectHmacSignature(RejectedHmac):
    pass


class IncorrectHmacContentHash(RejectedHmac):
    pass


###
# private helpers


def _reconstruct_string_to_sign_from_request(
    request: HttpRequest, signed_headers: dict[str, str]
) -> str:
    signed_segments = [request.method, request.path]
    query_string = request.META.get("QUERY_STRING")
    if query_string:
        signed_segments.append(query_string)
    signed_segments.extend(signed_headers.values())
    return "\n".join(segment for segment in signed_segments if segment)


def _sign_message(message: str, hmac_key: str) -> str:
    encoded_message = base64.b64encode(message.encode())
    return hmac.new(
        key=hmac_key.encode(), digestmod=hashlib.sha256, msg=encoded_message
    ).hexdigest()


def _get_signed_components(
    request_url: str,
    request_method: str,
    request_content: bytes,
    additional_headers: dict[str, str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    parsed_url = urllib.parse.urlparse(request_url)
    content_hash = (
        hashlib.sha256(request_content).hexdigest() if request_content else None
    )
    auth_timestamp = datetime.now(UTC).isoformat()
    possible_signed_segments = [
        request_method,
        parsed_url.path,
        parsed_url.query,
        auth_timestamp,
        content_hash,
    ]
    signed_headers = {TIMESTAMP_HEADER: auth_timestamp}
    if content_hash:
        signed_headers[CONTENT_HASH_HEADER] = content_hash
    if additional_headers:
        # order matters, so append additional headers at the end for consistency
        possible_signed_segments.extend(additional_headers.values())
        signed_headers.update(additional_headers)
    # Filter out query string and content_hash if none present
    signed_segments = [segment for segment in possible_signed_segments if segment]
    return signed_segments, signed_headers


def _validate_timestamp(signed_timestamp: str | None, expiration_seconds: int) -> None:
    if not signed_timestamp:
        raise UnsupportedHmacAuthorization(
            f"HMAC Signed Request missing expected signed header '{TIMESTAMP_HEADER}'"
        )
    expiration_time = datetime.now(UTC) - timedelta(seconds=expiration_seconds)
    request_time = datetime.fromisoformat(signed_timestamp)
    if request_time < expiration_time:
        raise ExpiredHmacTimestamp(
            f"HMAC Signed Request is too old (expected at most {expiration_seconds} seconds)"
        )
    elif request_time > datetime.now(UTC):
        raise FutureHmacTimestamp(
            "HMAC Signed Request provided a timestamp from the future"
        )


def _validate_content_hash(sha256_hexdigest: str, request_content: bytes) -> None:
    if sha256_hexdigest and not hmac.compare_digest(
        sha256_hexdigest, hashlib.sha256(request_content).hexdigest()
    ):
        raise IncorrectHmacContentHash(
            "Computed content hash did not match value from headers"
        )
