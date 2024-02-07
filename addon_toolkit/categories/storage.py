import enum

from addon_toolkit import (
    AddonCategory,
    AddonInterface,
    PagedResult,
    proxy_operation,
    redirect_operation,
)


__all__ = ("StorageAddonCategory",)


class StorageCapability(enum.StrEnum):
    ACCESS = "access"
    BROWSE = "browse"
    UPDATE = "update"
    COMMIT = "commit"


# what a base StorageInterface could be like (incomplete)
class StorageInterface(AddonInterface):
    ##
    # "item-read" operations:

    @redirect_operation(capability=StorageCapability.ACCESS)
    def item_download_url(self, item_id: str) -> str:
        raise NotImplementedError  # e.g. waterbutler url, when appropriate

    @proxy_operation(capability=StorageCapability.ACCESS)
    async def get_item_description(self, item_id: str) -> dict:
        raise NotImplementedError

    ##
    # "item-write" operations:

    @redirect_operation(capability=StorageCapability.UPDATE)
    def item_upload_url(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.UPDATE)
    async def pls_delete_item(self, item_id: str):
        raise NotImplementedError

    ##
    # "tree-read" operations:

    @proxy_operation(capability=StorageCapability.BROWSE)
    async def get_root_item_ids(self) -> PagedResult:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.BROWSE)
    async def get_parent_item_id(self, item_id: str) -> str | None:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.BROWSE)
    async def get_item_path(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.BROWSE)
    async def get_child_item_ids(self, item_id: str) -> PagedResult:
        raise NotImplementedError

    ##
    # "tree-write" operations

    @proxy_operation(capability=StorageCapability.UPDATE)
    async def pls_move_item(self, item_id: str, new_treepath: str):
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.UPDATE)
    async def pls_copy_item(self, item_id: str, new_treepath: str):
        raise NotImplementedError

    ##
    # "version-read" operations

    @proxy_operation(capability=StorageCapability.ACCESS)
    async def get_current_version_id(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapability.ACCESS)
    async def get_version_ids(self, item_id: str) -> PagedResult:
        raise NotImplementedError

    ##
    # "version-write" operations

    @proxy_operation(capability=StorageCapability.UPDATE)
    async def pls_restore_version(self, item_id: str, version_id: str):
        raise NotImplementedError


StorageAddonCategory = AddonCategory(
    capabilities=StorageCapability,
    base_interface=StorageInterface,
)
