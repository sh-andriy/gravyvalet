import base64
import hashlib
import hmac
import re
import urllib
from datetime import (
    UTC,
    datetime,
    timedelta,
)

from django.conf import settings


def _sign_message(message, hmac_key=None):
    key = hmac_key or settings.DEFAULT_HMAC_KEY
    encoded_message = base64.b64encode(message.encode())
    return hmac.new(
        key=key.encode(), digestmod=hashlib.sha256, msg=encoded_message
    ).hexdigest()


def _get_signed_components(request_url, request_method, body):
    parsed_url = urllib.parse.urlparse(request_url)
    content_hash = hashlib.sha256(body.encode()).hexdigest if body else None
    auth_timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    signed_segments = [
        request_method,
        parsed_url.path,
        parsed_url.query,
        auth_timestamp,
        content_hash,
    ]
    # Filter out query string and content_hash if none present
    signed_segments = [segment for segment in signed_segments if segment]
    signed_headers = {"X-Authorization-Timestamp": auth_timestamp}
    if content_hash:
        signed_headers["X-Content-SHA256"] = content_hash
    return signed_segments, signed_headers


def make_signed_headers(
    request_url, request_method, body="", hmac_key=None, ttl_seconds=110
):
    signed_string_segments, signed_headers = _get_signed_components(
        request_url, request_method, body
    )
    signature = _sign_message(
        message="\n".join(signed_string_segments), hmac_key=hmac_key
    )

    signature_header_fields = ";".join(signed_headers.keys())
    auth_header_value = (
        f"HMAC-SHA256 SignedHeaders={signature_header_fields}&Signature={signature}"
    )
    return dict(
        **signed_headers,
        **{
            "X-Message-Expiration": datetime.now(UTC) + timedelta(seconds=ttl_seconds),
            "Authorization": auth_header_value,
        },
    )


def _reconstruct_string_to_sign_from_request(request):
    signed_segments = [
        request.method,
        request.path,
        request.query_params.urlencode(),
        request.headers["X-Authorization-Timestamp"],
        request.headers.get("X-Content-SHA256"),
    ]
    return "\n".join([segment for segment in signed_segments if segment])


def validate_signed_headers(request, hmac_key=None):
    signature_parse_expression = re.compile(
        r"^HMAC-SHA256 .*Signature=(?P<signature>[^\W_]*$)"
    )
    match = signature_parse_expression.match(request.headers.get("Authorization", ""))
    if not match:
        raise ValueError(
            "Message was not authorized via valid HMAC-SHA256 signed heders"
        )
    expected_signature = match.group("signature")

    computed_signature = _sign_message(
        message=_reconstruct_string_to_sign_from_request(request), hmac_key=hmac_key
    )
    if not hmac.compare_digest(computed_signature, expected_signature):
        raise ValueError("Could not verify HMAC signed request")

    content_hash = request.headers.get("X-Content-SHA256")
    if content_hash and hashlib.sha256(request.body).hexdigest() != content_hash:
        raise ValueError("Local content hash did not match value from headers")
