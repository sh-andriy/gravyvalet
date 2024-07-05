from http import HTTPStatus

from asgiref.sync import async_to_sync
from django.http import HttpResponse

from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.common.known_imps import AddonImpNumbers
from addon_service.oauth1.utils import get_access_token
from addon_service.oauth_utlis import update_external_account_ids


def oauth1_callback_view(request):
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
    async_to_sync(update_external_account_ids)([account])
