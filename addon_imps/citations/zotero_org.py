from addon_toolkit.interfaces.storage import StorageAddonImp


class ZoteroOrgCitationImp(StorageAddonImp):
    async def get_external_account_id(self, auth_result_extras: dict[str, str]) -> str:
        return auth_result_extras["userID"]
