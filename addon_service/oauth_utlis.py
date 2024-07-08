from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_service.common.network import GravyvaletHttpRequestor


async def update_external_account_ids(accounts):
    for _account in accounts:
        _account.external_account_id = await _account.imp_cls.get_external_account_id(
            network=GravyvaletHttpRequestor(
                client_session=await get_singleton_client_session(),
                prefix_url=_account.external_service.api_base_url,
                account=_account,
            ),
        )
        await _account.asave()
