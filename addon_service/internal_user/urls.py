from addon_service.common.jsonapi import urls_for_viewset

from . import views


urlpatterns = urls_for_viewset(
    views.InternalUserViewSet,
    views.InternalUserRelationshipView,
)
