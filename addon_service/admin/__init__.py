from django.contrib import admin

from addon_service import models

from ._base import ModelAdminWithLinks


@admin.register(models.ExternalStorageService)
class ExternalStorageServiceAdmin(ModelAdminWithLinks):
    readonly_fields = (
        "id",
        "created",
        "modified",
    )
    linked_fk_fields = ("oauth2_client_config",)
    list_display = ("name", "id", "created", "modified")


@admin.register(models.OAuth2ClientConfig)
class OAuth2ClientConfigAdmin(ModelAdminWithLinks):
    readonly_fields = (
        "id",
        "created",
        "modified",
    )


# TODO: if DEBUG?
# @admin.register(models.AuthorizedStorageAccount)
# class AuthorizedStorageAccountAdmin(ModelAdminWithLinks):
#     readonly_fields = (
#         'id',
#         'created',
#         'modified',
#     )
#
#
# @admin.register(models.ConfiguredStorageAddon)
# class ConfiguredStorageAddonAdmin(ModelAdminWithLinks):
#     readonly_fields = (
#         'id',
#         'created',
#         'modified',
#     )
