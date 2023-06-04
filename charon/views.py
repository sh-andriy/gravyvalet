import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader

from . import utils
from serializer import BoxSerializer

logger = logging.getLogger(__name__)


# ========== VIEWS ==========


def index(request):
    return HttpResponse(
        "Hello, world. Welcome to the continental, rated two stars on tripadvisor."
    )


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


def box_user_auth(request, project_guid):
    if request.method == 'PUT':
        _box_import_auth(request, project_guid)
    elif request.method = 'DELETE':
        _box_deauthorize_node(request, project_guid)

    raise HttpResponse('Method Not Allowed', status=405)

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

    # kwargs ib:({'pid': 'dve82', 'parent': None,
    #   'node': (title='Provider - S3', category='project') with guid 'dve82'})

    # inflate node
    node = utils._get_node_by_guid(project_guid)

    # inflate user
    user = utils._get_user_by_auth(request)
    if user is None:
        raise HttpResponse('Unauthorized', status=401)

    addon_name = 'box'
    query_params = request.GET
    kwargs = {**query_params}
    kwargs['project_guid'] = project_guid
    kwargs['node'] = node

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
    kwargs['auth_user'] = Auth.from_kwargs(request.args.to_dict(), kwargs)
    auth_user = kwargs['auth_user'].user
    # User must be logged in
    if auth_user is None:
        raise HttpResponse('Unauthorized', status=401)
    # User must have permissions
    if not node.has_permission(auth_user, 'WRITE'):
        raise HttpResponseForbidden('User has not permissions on node')

    # ====> @must_have_addon('box', 'user')
    user_addon = auth_user.get_addon(addon_name)
    if user_addon is None:
        raise HttpResponseBadRequest('No user addon found')

    # ====> @must_have_addon('box', 'node')
    node_addon = node.get_addon(addon_name)
    if node_addon is None:
        raise HttpResponseBadRequest('No node addon found')

    external_account = ExternalAccount.load(request.json['external_account_id'])

    if not user_addon.external_accounts.filter(id=external_account.id).exists():
        raise HttpResponseForbidden('User has no such account')

    try:
        node_addon.set_auth(external_account, user_addon.owner)
    except PermissionsError:
        raise HttpResponseForbidden('Unable to apply users auth to node')

    node_addon.save()

    return {
        'result': BoxSerializer().serialize_settings(node_addon, auth_user),
        'message': 'Successfully imported access token from profile.',
    }

def _box_deauthorize_node(request, project_guid):
    return {}


def box_folders_list(request, project_guid):
    return {}


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


def box_account_list(request):
    """
    from addons.views.generic_views.account_list
    box versions currys above with args ('box', BoxSerializer)

    impl based off of addons.base.generic_views._account_list
    @must_be_logged_in decorator injects `auth` into call
    """

    # must_be_logged_in impl inlined
    auth = Auth.from_kwargs(request.args.to_dict(), kwargs)
    if not auth.logged_in:
        return redirect(cas.get_login_url(request.url))

    user_settings = auth.user.get_addon(addon_short_name)
    serializer = BoxSerializer(user_settings=user_settings)
    return Boxserializer.serialized_user_settings

def get_project_settings_for_box(request, project_guid):
    if request.method == 'GET':
        _box_get_config(request, project_guid)
    elif request.method = 'PUT':
        _box_set_config(request, project_guid)

    raise HttpResponse('Method Not Allowed', status=405)

def _box_get_config(request, project_guid):
    """
    from addons.views.generic_views.get_config
    box versions currys above with args ('box', BoxSerializer)

    impl based off of addons.base.generic_views._get_config
    @must_be_logged_in             decorator injects `auth` into call
    @must_have_addon('node')       decorator does ???
    @must_be_valid_project         decorator does ???
    @must_have_permission('WRITE') decorator does ???

    _get_config docstring
    API that returns the serialized node settings.
    """
    node_addon = None  # TODO: where this come from?
    auth = None  # TODO: injected bu must_be_logged_in
    return {
        'result': BoxSerializer().serialize_settings(
            node_addon,
            auth.user
        )
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
        uid = folder['id']
        node_addon.set_folder(uid, auth=auth)
        node_addon.save()

    node_addon = None  # TODO: where this come from?
    user_addon = None  # TODO: where this come from?
    auth = None  # TODO: injected by must_be_logged_in

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
            'urls': BoxSerializer(node_settings=node_addon).addon_serialized_urls,
        },
        'message': 'Successfully updated settings.',
    }

def get_project_addons(request, project_guid):
    return {}
