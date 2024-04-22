import dataclasses
import enum

from rest_framework_json_api import serializers

from addon_service import models as db
from addon_service.common import known_imps
from addon_service.common.enum_decorators import enum_names_same_as
from addon_toolkit import (
    AddonImp,
    credentials,
    json_arguments,
)


@enum_names_same_as(known_imps._KnownAddonImps)
class WaterbutlerProviderKey(enum.Enum):
    BOX_DOT_COM = "box"

    if __debug__:
        BLARG = "blarrrg"

    @staticmethod
    def for_imp_cls(imp_cls: type[AddonImp]) -> str:
        _imp_name = known_imps.get_imp_name(imp_cls)
        _provider_key = WaterbutlerProviderKey[_imp_name].value
        if _provider_key is None:
            raise ValueError(imp_cls)
        return _provider_key


@dataclasses.dataclass
class WaterbutlerAddonSettings:
    external_api_url: str
    connected_root_id: str  # may be path or id
    waterbutler_provider_key: str
    external_account_id: str | None = None


class WaterButlerConfigurationSerializer(serializers.Serializer):
    """Serialize ConfiguredStorageAddon information required by WaterButler.

    The returned data should share a shape with the existing `serialize_waterbutler_credentials`
    and `serialize_waterbutler_settings` functions used by the OSF-based Addons.
    """

    credentials = serializers.SerializerMethodField("_credentials_for_waterbutler")
    settings = serializers.SerializerMethodField("_settings_for_waterbutler")

    def _credentials_for_waterbutler(
        self,
        configured_storage_addon: db.ConfiguredStorageAddon,
    ):
        _creds_data = configured_storage_addon.credentials
        match type(_creds_data):
            case credentials.AccessTokenCredentials:
                return {"token": _creds_data.access_token}
            case (
                credentials.AccessKeySecretKeyCredentials
                | credentials.UsernamePasswordCredentials
            ):
                # field names line up with waterbutler's expectations
                return dataclasses.asdict(_creds_data)
            case _:
                raise ValueError(f"unknown credentials type: {_creds_data}")

    def _settings_for_waterbutler(
        self,
        configured_storage_addon: db.ConfiguredStorageAddon,
    ):
        """An ugly compatibility layer between GravyValet and WaterButler."""
        _wb_addon_settings = WaterbutlerAddonSettings(
            external_api_url=configured_storage_addon.base_account.api_base_url,
            connected_root_id=configured_storage_addon.root_folder,
            waterbutler_provider_key=WaterbutlerProviderKey.for_imp_cls(
                configured_storage_addon.external_service.addon_imp.imp_cls
            ),
            external_account_id=configured_storage_addon.base_account.external_account_id,
        )
        return json_arguments.json_for_dataclass(_wb_addon_settings)
