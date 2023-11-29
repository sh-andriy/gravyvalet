from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_json_api.utils import get_resource_type_from_serializer


def urls_for_viewset(viewset, relationship_view=None, additional_urlpatterns=()):
    _resource_name = get_resource_type_from_serializer(viewset.serializer_class)
    _router = SimpleRouter()
    _router.register(
        prefix=_resource_name,
        viewset=viewset,
        basename=_resource_name,
    )
    _urlpatterns = [*_router.urls]
    _urlpatterns.append(
        path(
            f"{_resource_name}/<pk>/<related_field>/",
            viewset.as_view({"get": "retrieve_related"}),
            name=f"{_resource_name}-related",
        ),
    )
    if relationship_view is not None:
        _urlpatterns.append(
            path(
                f"{_resource_name}/<pk>/relationships/<related_field>/",
                relationship_view.as_view(),
                name=f"{_resource_name}-relationships",
            ),
        )

    # _urlpatterns.extend(additional_urlpatterns)
    return _urlpatterns
