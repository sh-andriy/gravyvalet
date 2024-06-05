from http import HTTPStatus

from asgiref.sync import sync_to_async
from django.db import transaction
from django.http import HttpResponse

from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_service.common.network import GravyvaletHttpRequestor
from addon_service.models import (
    OAuth2ClientConfig,
    OAuth2TokenMetadata,
)
from addon_service.oauth.utils import get_initial_access_token


@transaction.non_atomic_requests  # async views and ATOMIC_REQUESTS do not mix
async def oauth2_callback_view(request):
    """
    Handles oauth callbacks for the GV

    see https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2
    """

    # TODO: handle error: https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2.1
    _state_token = request.GET["state"]
    _authorization_code = request.GET["code"]
    _token_metadata, _oauth_client_config = await _resolve_state_token(_state_token)
    _fresh_token_result = await get_initial_access_token(
        token_endpoint_url=_oauth_client_config.token_endpoint_url,
        authorization_code=_authorization_code,
        auth_callback_url=_oauth_client_config.auth_callback_url,
        client_id=_oauth_client_config.client_id,
        client_secret=_oauth_client_config.client_secret,
    )
    _accounts = await _token_metadata.update_with_fresh_token(_fresh_token_result)
    await _update_external_account_ids(_accounts)
    return HttpResponse(status=HTTPStatus.OK)  # TODO: redirect


###
# module-private helpers


@sync_to_async
def _resolve_state_token(
    state_token: str,
) -> tuple[OAuth2TokenMetadata, OAuth2ClientConfig]:
    _token_metadata = OAuth2TokenMetadata.objects.get_by_state_token(state_token)
    return (_token_metadata, _token_metadata.client_details)


async def _update_external_account_ids(accounts):
    for _account in accounts:
        _account.external_account_id = await _account.imp_cls.get_external_account_id(
            network=GravyvaletHttpRequestor(
                client_session=await get_singleton_client_session(),
                prefix_url=_account.external_service.api_base_url,
                account=_account,
            ),
        )
        await sync_to_async(_account.save)()
