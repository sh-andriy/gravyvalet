from http import HTTPStatus

from asgiref.sync import (
    async_to_sync,
    sync_to_async,
)
from django.http import HttpResponse

from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_service.common.known_imps import AddonImpNumbers
from addon_service.common.network import GravyvaletHttpRequestor
from addon_service.models import (
    OAuth2ClientConfig,
    OAuth2TokenMetadata,
)
from addon_service.oauth1.utils import get_access_token


def oauth1_callback_view(request):
    print(f"{request.headers}=")
    oauth_token = request.GET["oauth_token"]
    oauth_verifier = request.GET["oauth_verifier"]

    pk = request.session.get("oauth1a_account_id")
    del request.session["oauth1a_account_id"]

    account = AuthorizedStorageAccount.objects.get(pk=pk)

    oauth1_client_config = account.external_service.oauth1_client_config
    final_credentials, other_info = async_to_sync(get_access_token)(
        oauth1_client_config.access_token_url,
        oauth1_client_config.client_key,
        oauth1_client_config.client_secret,
        oauth_token,
        account.credentials.oauth_token_secret,
        oauth_verifier,
    )
    account.credentials = final_credentials
    account.is_oauth1_ready = True
    account.save()
    update_account_with_additional_data(account, other_info)
    return HttpResponse(status=HTTPStatus.OK)  # TODO: redirect


def update_account_with_additional_data(account: AuthorizedStorageAccount, data: dict):
    match account.external_service.int_addon_imp:
        case AddonImpNumbers.ZOTERO_ORG:
            account.external_account_id = data["userID"]
    account.save()
    _update_external_account_ids([account])


###
# module-private helpers


@sync_to_async
def _resolve_state_token(
    state_token: str,
) -> tuple[OAuth2TokenMetadata, OAuth2ClientConfig]:
    _token_metadata = OAuth2TokenMetadata.objects.get_by_state_token(state_token)
    return (_token_metadata, _token_metadata.client_details)


@async_to_sync
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
