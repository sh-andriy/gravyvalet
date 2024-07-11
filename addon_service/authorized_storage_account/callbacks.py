from addon_service.addon_imp.instantiation import get_storage_addon_instance
from addon_service.authorized_storage_account.models import AuthorizedStorageAccount


async def after_successful_auth(
    account: AuthorizedStorageAccount,
    auth_result_extras: dict[str, str] | None = None,
):
    _imp = await get_storage_addon_instance(
        account.imp_cls,  # type: ignore[arg-type]
        account,
        account.storage_imp_config(),
    )
    account.external_account_id = await _imp.get_external_account_id(
        auth_result_extras or {}
    )
    await account.asave()
