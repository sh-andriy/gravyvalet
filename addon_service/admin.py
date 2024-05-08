from django.contrib import admin

from addon_service import models


admin.site.register(models.AuthorizedStorageAccount)
admin.site.register(models.ConfiguredStorageAddon)
admin.site.register(models.ExternalStorageService)
admin.site.register(models.OAuth2ClientConfig)
