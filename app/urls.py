"""gravyvalet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from addon_service import views


router = DefaultRouter()


def _register_viewset(viewset):
    """convenience for viewsets with `resource_name`"""
    router.register(viewset.resource_name, viewset)


_register_viewset(views.AuthorizedStorageAccountViewSet)
_register_viewset(views.ConfiguredStorageAddonViewSet)
_register_viewset(views.InternalResourceViewSet)


urlpatterns = [
    path("v1/", include(router.urls)),
]
