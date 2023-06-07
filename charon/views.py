import logging

from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import redirect
from django.template import loader

from . import models, serializer, utils

logger = logging.getLogger(__name__)

# ========== VIEWS ==========


def index(request):
    return HttpResponse(
        "Hello, world. Welcome to the continental, rated two stars on tripadvisor."
    )


# pretend to connect to box, but we lie
def connect_box(request):
    logger.error('@@@ got request for connect_box')
    logger.error('@@@   request ib:({})'.format(request))

    # user = utils._get_user(request)
    # auth_url_base = 'https://www.box.com/api/oauth2/authorize'
    # callback_url = 'https://www.box.com/api/oauth2/token'

    # return HttpResponse("You tried to box, but box we didn't.")
    response = redirect(callback_box)
    response['Cross-Origin-Opener-Policy'] = 'unsafe-none'
    return response


# pretend like we were called back from box, but we lie
def callback_box(request):
    logger.error('@@@ got request for callback_box')
    logger.error('@@@   request ib:({})'.format(request))
    logger.error('@@@   headers are:({})'.format(request.headers))
    template = loader.get_template('charon/callback.html')
    user = utils._get_user(request)
    context = {'user_id': user['id'] if user else '*no user id*'}
    return HttpResponse(
        template.render(context, request),
        headers={'Cross-Origin-Opener-Policy': 'unsafe-none'},
    )


def box_account_list(request):
    """
    from addons.views.generic_views.account_list
    box versions currys above with args ('box', BoxSerializer)

    impl based off of addons.base.generic_views._account_list
    @must_be_logged_in decorator injects `auth` into call
    """

    # must_be_logged_in impl inlined
    # auth = Auth.from_kwargs(request.args.to_dict(), kwargs)
    auth = _get_auth_from_request(request)
    if not auth.logged_in:
        return redirect(utils.cas_get_login_url(request.url))

    user_settings = auth.user.get_addon('box')
    our_serializer = serializer.BoxSerializer(user_settings=user_settings)
    return our_serializer.serialized_user_settings


def box_project_config(request, project_guid):
    if request.method == 'GET':
        _box_get_config(request, project_guid)
    elif request.method == 'PUT':
        _box_set_config(request, project_guid)

    return HttpResponse('Method Not Allowed', status=405)


def box_user_auth(request, project_guid):
    if request.method == 'PUT':
        _box_import_auth(request, project_guid)
    elif request.method == 'DELETE':
        _box_deauthorize_node(request, project_guid)

    return HttpResponse('Method Not Allowed', status=405)


def box_folder_list(request, project_guid):
    """
    based off of addons.box.views.box_folder_list

    *DOESN'T impl or curry generic_views.folder_list or _folder_list*

    impl based off of addons.box.views.box_folder_list

    inlined decorators from website.project.decorators:
    @must_have_addon('box', 'node')  decorator injects node_addon
    @must_be_addon_authorizer('box') decorator does ???

    Returns all the subsequent folders under the folder id passed.
    """
    # TODO: how exactly is this different from generic_views.folder_list curried method?
    # inflate node
    node = utils._get_node_by_guid(project_guid)
    addon_name = 'box'
    node_addon = _get_node_addon_for_node(node, addon_name)
    folder_id = request.args.get('folder_id')
    return node_addon.get_folders(folder_id=folder_id)


# from website.routes, view is website.project.views.node.node_choose_addons
#   which calls .config_addons() on node model object
#   .config_addons() is defined in AddonModelMixin
def get_project_addons(request, project_guid):
    return JsonResponse(['box'])


def _box_get_config(request, project_guid):
    """
    from addons.views.generic_views.get_config
    box versions currys above with args ('box', BoxSerializer)

    impl based off of addons.base.generic_views._get_config
    @must_be_logged_in              decorator injects `auth` into call
    @must_have_addon('box', 'node') decorator does ???
    @must_be_valid_project          decorator does ???
    @must_have_permission('WRITE')  decorator does ???

    _get_config docstring
    API that returns the serialized node settings.
    """
    # auth was injected by @must_be_logged_in
    auth = _get_auth_from_request(request)
    # node_addon injected by @must_have_addon('box', 'node')
    node = utils._get_node_by_guid(project_guid)
    addon_name = 'box'
    node_addon = _get_node_addon_for_node(node, addon_name)
    return {
        'result': serializer.BoxSerializer().serialize_settings(node_addon, auth.user)
    }


def _box_set_config(request, project_guid):
    """
    from addons.views.generic_views.set_config
    box versions currys above with args ('box', 'Box', BoxSerializer, _set_folder())

    impl based off of addons.base.generic_views._set_config
    @must_not_be_registration
    @must_have_addon('user')     decorator does ???
    @must_have_addon('node')     decorator does ???
    @must_be_addon_authorizer    decorator does ???
    @must_have_permission(WRITE) decorator does ???

    _set_config docstring
    View for changing a node's linked folder.
    """

    def set_folder(node_addon, folder, auth):
        uid = folder['id']  # TODO: why called `uid`?
        node_addon.set_folder(uid, auth=auth)
        node_addon.save()

    # auth was injected by @must_be_logged_in
    auth = _get_auth_from_request(request)
    user = auth.user

    # node_addon injected by @must_have_addon('box', 'node')
    node = utils._get_node_by_guid(project_guid)
    addon_name = 'box'
    node_addon = _get_node_addon_for_node(node, addon_name)

    # user_addon injected by @must_have_addon('box', 'user')
    user_addon = _get_user_addon_for_user(user)  # TODO: we dont use it?

    folder = request.json.get('selected')  # TODO: flask syntax?
    set_folder(node_addon, folder, auth)

    path = node_addon.folder_path

    folder_name = None
    if path != '/':
        folder_name = path.replace('All Files', '')
    else:
        folder_name = '/ (Full {0})'.format('Box')

    return {
        'result': {
            'folder': {
                'name': folder_name,
                'path': path,
            },
            'urls': serializer.BoxSerializer(
                node_settings=node_addon
            ).addon_serialized_urls,
        },
        'message': 'Successfully updated settings.',
    }


def _box_import_auth(request, project_guid):
    """
    based off of addons.base.generic_views.import_auth
    box versions currys above with args ('box', BoxSerializer)

    impl based off of addons.base.generic_views._import_auth

    inlined decorators from website.project.decorators:
    must_have_permission
    must_have_addon
    """
    logger.error('### in import_auth_box! request ib:({})'.format(request.json))

    # query_params = request.GET
    # kwargs = {**query_params}
    # kwargs['project_guid'] = project_guid
    # kwargs['node'] = node
    # kwargs in osf:({'pid': 'dve82', 'parent': None,
    #   'node': (title='Provider - S3', category='project') with guid 'dve82'})

    # ===> utils._verify_permissions('WRITE', user, node, kwargs)
    # Auth defined in frameworks.auth.core.Auth
    #   three params:
    #     self.user = user
    #     self.api_node = api_node
    #     self.private_key = private_key
    #   @prop.logged_in
    #   @prop.private_link
    #   def from_kwargs(cls, request_args, kwargs):
    #     user = request_args.get('user') or kwargs.get('user') or _get_current_user()
    #     private_key = request_args.get('view_only')
    #     cls(user=user, private_key=private_key)
    # kwargs['auth_user'] = Auth.from_kwargs(request.args.to_dict(), kwargs)
    # auth_user = kwargs['auth_user'].user
    auth = _get_auth_from_request(request)
    user = auth.user

    # inflate node
    node = utils._get_node_by_guid(project_guid)

    addon_name = 'box'

    # User must be logged in
    if user is None:
        raise HttpResponse('Unauthorized', status=401)

    # User must have permissions
    if not node.has_permission(user, 'WRITE'):
        raise HttpResponseForbidden('User has not permissions on node')

    # ====> @must_have_addon('box', 'user')
    user_addon = user.get_addon(addon_name)
    if user_addon is None:
        raise HttpResponseBadRequest('No user addon found')

    # ====> @must_have_addon('box', 'node')
    node_addon = node.get_addon(addon_name)
    if node_addon is None:
        raise HttpResponseBadRequest('No node addon found')

    external_account = models.ExternalAccount.load(request.json['external_account_id'])

    if not user_addon.external_accounts.filter(id=external_account.id).exists():
        raise HttpResponseForbidden('User has no such account')

    try:
        node_addon.set_auth(external_account, user_addon.owner)
    except utils.PermissionsError:
        raise HttpResponseForbidden('Unable to apply users auth to node')

    node_addon.save()

    return {
        'result': serializer.BoxSerializer().serialize_settings(node_addon, user),
        'message': 'Successfully imported access token from profile.',
    }


def _box_deauthorize_node(request, project_guid):
    """
    based off of addons.base.generic_views.deauthorize_node
    box versions currys above with args ('box')

    impl based off of addons.base.generic_views._deauthorize_node

    inlined decorators from website.project.decorators:
    @must_not_be_registration    decorator does ???
    @must_have_addon('node')     decorator does ???
    @must_have_permission(WRITE) decorator does ???
    """
    auth = _get_auth_from_request(request)

    # inflate node
    node = utils._get_node_by_guid(project_guid)
    addon_name = 'box'
    node_addon = node.get_addon(addon_name)

    node_addon.deauthorize(auth=auth)
    node_addon.save()
    return None


def _get_auth_from_request(request):
    # TODO: i think this basically inlines @must_be_logged_in
    # did I start doing this with get_credentials?
    # i think so
    return {}


# reimplementation of @must_have_addon('addon_name', 'node')
# broken out in case there is other validation to be incorporated from the decorator
def _get_node_addon_for_node(node, addon_name):
    return node.get_addon(addon_name)


# reimplementation of @must_have_addon('addon_name', 'node')
# broken out in case there is other validation to be incorporated from the decorator
def _get_user_addon_for_user(user, addon_name):
    return user.get_addon(addon_name)


# take a project guid and inflate it into a node object
def _get_node_by_guid(project_guid):
    return getattr(models.Guid.load(project_guid), 'referent', None)


# not currently being used
def get_credentials(request):
    logger.error('@@@ got request for get_credentials')

    user = utils._get_user(request)
    # check_access(node, auth, action, cas_resp)
    # provider_settings = None
    # if hasattr(node, 'get_addon'):
    #     provider_settings = node.get_addon(provider_name)
    #     if not provider_settings:
    #         raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    node_id = None
    node_props = utils._get_node_properties(node_id)
    creds_and_settings = utils._lookup_creds_and_settings_for(user['id'], node_props)
    callback_url = utils._make_osf_callback_url(node_props)
    return utils._make_wb_auth_payload(user, creds_and_settings, callback_url)
