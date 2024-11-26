from asgiref.sync import async_to_sync
from rest_framework_json_api import serializers

from addon_service.addon_imp.instantiation import get_storage_addon_instance__blocking
from addon_service.configured_addon.storage.models import ConfiguredStorageAddon
from addon_toolkit import (
    credentials,
    json_arguments,
)


class WaterButlerConfigSerializer(serializers.Serializer):
    """Serialize ConfiguredStorageAddon information required by WaterButler.

    The returned data should share a shape with the existing `serialize_waterbutler_credentials`
    and `serialize_waterbutler_settings` functions used by the OSF-based Addons.
    """

    class JSONAPIMeta:
        resource_name = "waterbutler-config"

    credentials = serializers.SerializerMethodField("_credentials_for_waterbutler")
    config = serializers.SerializerMethodField("_config_for_waterbutler")

    def _credentials_for_waterbutler(self, configured_storage_addon):
        _creds_data = configured_storage_addon.credentials
        config = configured_storage_addon.config
        host_url = config.external_api_url

        match type(_creds_data):
            case credentials.AccessTokenCredentials:
                return {"token": _creds_data.access_token, "host": host_url}
            case (
                credentials.AccessKeySecretKeyCredentials
                | credentials.UsernamePasswordCredentials
            ):
                # field names line up with waterbutler's expectations
                serialized_creds = json_arguments.json_for_dataclass(_creds_data)
                serialized_creds["host"] = host_url
            case _:
                raise ValueError(f"unknown credentials type: {_creds_data}")

    def _config_for_waterbutler(self, configured_storage_addon: ConfiguredStorageAddon):
        imp = get_storage_addon_instance__blocking(
            configured_storage_addon.imp_cls,
            configured_storage_addon.base_account,
            configured_storage_addon.config,
        )
        return async_to_sync(imp.build_wb_config)()
