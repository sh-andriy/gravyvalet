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
    # GET is $addon_account_list
    path(
        'settings/box/accounts/',
        views.box_account_list,
        name='box_account_list',
    ),
    # GET is $addon_get_config
    # PUT is $addon_set_config
    path(
        'projects/<str:project_guid>/box/settings/',
        views.get_project_settings_for_box,
        name='get_project_settings_for_box',
    ),
    # PUT is $addon_import_auth
    # DELETE is $addon_deauthorize_node
    path(
        'projects/<str:project_guid>/box/user_auth/',
        views.box_user_auth,
        name='box_user_auth',
    ),
    # GET is $addon_folders_list
    path(
        'projects/<str:project_guid>/box/folders/',
        views.box_folder_list,
        name='box_folder_list',
    ),
    # not specified in addons.base.views
    # from website.routes, view is website.project.views.node.node_choose_addons
    #   which calls .config_addons() on node model object
    #   .config_addons() is defined in AddonModelMixin
    path(
        'projects/<str:project_guid>/settings/addons/',
        views.get_project_addons,
        name='get_project_addons',
    ),
]
