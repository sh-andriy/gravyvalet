from django.contrib import admin

from addon_service import models
from addon_service.common import known_imps
from addon_service.common.credentials_formats import CredentialsFormats
from addon_service.common.service_types import ServiceTypes

from ._base import GravyvaletModelAdmin


@admin.register(models.ExternalStorageService)
class ExternalStorageServiceAdmin(GravyvaletModelAdmin):
    list_display = ("name", "created", "modified")
    readonly_fields = (
        "id",
        "created",
        "modified",
    )
    linked_fk_fields = ("oauth2_client_config",)
    enum_choice_fields = {
        "int_addon_imp": known_imps.AddonImpNumbers,
        "int_credentials_format": CredentialsFormats,
        "int_service_type": ServiceTypes,
    }


@admin.register(models.OAuth2ClientConfig)
class OAuth2ClientConfigAdmin(GravyvaletModelAdmin):
    readonly_fields = (
        "id",
        "created",
        "modified",
    )
