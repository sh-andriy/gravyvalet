from asgiref.sync import async_to_sync

from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_service.common.network import GravyvaletHttpRequestor
from addon_service.models import AuthorizedStorageAccount
from addon_toolkit.interfaces.storage import (
    StorageAddonImp,
    StorageConfig,
)


async def get_storage_addon_instance(
    imp_cls: type[StorageAddonImp],
    account: AuthorizedStorageAccount,
    config: StorageConfig,
) -> StorageAddonImp:
    assert issubclass(imp_cls, StorageAddonImp)
    return imp_cls(
        config=config,
        network=GravyvaletHttpRequestor(
            client_session=await get_singleton_client_session(),
            prefix_url=config.external_api_url,
            account=account,
        ),
    )


get_storage_addon_instance__blocking = async_to_sync(get_storage_addon_instance)
