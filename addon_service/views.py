""" Import views/viewsets here for convenience """
from addon_service.authorized_storage_account.views import (
    AuthorizedStorageAccountRelationshipView,
    AuthorizedStorageAccountViewSet,
)
from addon_service.configured_storage_addon.views import (
    ConfiguredStorageAddonRelationshipView,
    ConfiguredStorageAddonViewSet,
)
from addon_service.external_storage_service.views import (
    ExternalStorageServiceRelationshipView,
    ExternalStorageServiceViewSet,
)
from addon_service.internal_resource.views import (
    InternalResourceRelationshipView,
    InternalResourceViewSet,
)
from addon_service.internal_user.views import (
    InternalUserRelationshipView,
    InternalUserViewSet,
)


__all__ = (
    "AuthorizedStorageAccountRelationshipView",
    "AuthorizedStorageAccountViewSet",
    "ConfiguredStorageAddonRelationshipView",
    "ConfiguredStorageAddonViewSet",
    "ExternalStorageServiceRelationshipView",
    "ExternalStorageServiceViewSet",
    "InternalResourceRelationshipView",
    "InternalResourceViewSet",
    "InternalUserRelationshipView",
    "InternalUserViewSet",
)
