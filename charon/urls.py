from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('box', views.connect_box, name='connect_box'),
    path('box/callback', views.callback_box, name='callback_box'),
    path('box/import_auth', views.import_auth_box, name='import_auth_box'),
    path('box/get_root_folder', views.get_root_folder_box, name='get_root_folder_box'),
    path(
        'box/get_folder_listing',
        views.get_folder_listing_box,
        name='get_folder_listing_box',
    ),
    path(
        'projects/<str:project_guid>/<str:addon_name>/settings/',
        views.get_project_settings,
        name='project_settings',
    ),
]
