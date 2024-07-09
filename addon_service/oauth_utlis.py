from addon_service.authorized_storage_account.models import AuthorizedStorageAccount
from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_service.common.network import GravyvaletHttpRequestor


async def update_external_account_id(account: AuthorizedStorageAccount):
    account.external_account_id = await account.imp_cls.get_external_account_id(
        network=GravyvaletHttpRequestor(
            client_session=await get_singleton_client_session(),
            prefix_url=account.external_service.api_base_url,
            account=account,
        ),
    )
    await account.asave()
