from primitive_metadata import primitive_rdf as rdf

from addon_toolkit import (
    AddonCapabilities,
    AddonCapability,
    AddonCategory,
    AddonInterface,
    PagedResult,
    proxy_operation,
    redirect_operation,
)
from addon_toolkit.namespaces import GRAVY


__all__ = ("StorageAddonCategory",)


class StorageCapabilities(AddonCapabilities):
    ACCESS = AddonCapability(
        iri=GRAVY.access_capability,
        label=rdf.literal("access capability", language="en"),
        comment=rdf.literal("allows access to data items", language="en"),
    )
    BROWSE = AddonCapability(
        iri=GRAVY.browse_capability,
        label=rdf.literal("browse capability", language="en"),
        comment=rdf.literal(
            "allows browsing relation graphs among items",
            language="en",
        ),
    )
    UPDATE = AddonCapability(
        iri=GRAVY.update_capability,
        label=rdf.literal("update capability", language="en"),
        comment=rdf.literal("allows updating and adding items", language="en"),
    )
    COMMIT = AddonCapability(
        iri=GRAVY.commit_capability,
        label=rdf.literal("commit capability", language="en"),
        comment=rdf.literal("allows ", language="en"),
    )


# what a base StorageInterface could be like (incomplete)
class StorageInterface(AddonInterface):
    ##
    # "item-read" operations:

    @redirect_operation(capability=StorageCapabilities.ACCESS)
    def item_download_url(self, item_id: str) -> str:
        raise NotImplementedError  # e.g. waterbutler url, when appropriate

    @proxy_operation(capability=StorageCapabilities.ACCESS)
    async def get_item_description(self, item_id: str) -> dict:
        raise NotImplementedError

    ##
    # "item-write" operations:

    @redirect_operation(capability=StorageCapabilities.UPDATE)
    def item_upload_url(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.UPDATE)
    async def pls_delete_item(self, item_id: str):
        raise NotImplementedError

    ##
    # "tree-read" operations:

    @proxy_operation(capability=StorageCapabilities.BROWSE)
    async def get_root_item_ids(self) -> PagedResult:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.BROWSE)
    async def get_parent_item_id(self, item_id: str) -> str | None:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.BROWSE)
    async def get_item_path(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.BROWSE)
    async def get_child_item_ids(self, item_id: str) -> PagedResult:
        raise NotImplementedError

    ##
    # "tree-write" operations

    @proxy_operation(capability=StorageCapabilities.UPDATE)
    async def pls_move_item(self, item_id: str, new_treepath: str):
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.UPDATE)
    async def pls_copy_item(self, item_id: str, new_treepath: str):
        raise NotImplementedError

    ##
    # "version-read" operations

    @proxy_operation(capability=StorageCapabilities.ACCESS)
    async def get_current_version_id(self, item_id: str) -> str:
        raise NotImplementedError

    @proxy_operation(capability=StorageCapabilities.ACCESS)
    async def get_version_ids(self, item_id: str) -> PagedResult:
        raise NotImplementedError

    ##
    # "version-write" operations

    @proxy_operation(capability=StorageCapabilities.UPDATE)
    async def pls_restore_version(self, item_id: str, version_id: str):
        raise NotImplementedError


StorageAddonCategory = AddonCategory(
    capabilities=StorageCapabilities,
    base_interface=StorageInterface,
)
