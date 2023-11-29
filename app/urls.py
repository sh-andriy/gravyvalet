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

from addon_service.authorized_storage_account import urls as asa_urls
from addon_service.configured_storage_addon import urls as csa_urls
from addon_service.external_storage_service import urls as ess_urls
from addon_service.internal_resource import urls as ir_urls
from addon_service.internal_user import urls as iu_urls


urlpatterns = [
    path(
        "v1/",
        include(
            [
                *asa_urls.urlpatterns,
                *csa_urls.urlpatterns,
                *ess_urls.urlpatterns,
                *ir_urls.urlpatterns,
                *iu_urls.urlpatterns,
            ]
        ),
    ),
]
