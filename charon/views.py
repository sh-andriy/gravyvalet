import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from . import utils

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


def box_user_auth(request):
    """
    based off of addons.base.generic_views._import_auth
    inlined decorators from website.project.decorators:
    must_have_permission
    must_have_addon
    """
    logger.error('### in import_auth_box! request ib:({})'.format(request.json))

    node_id = ''
    target = kwargs.get('node') or getattr(
        Guid.load(kwargs.get('guid')), 'referent', None
    )

    kwargs['auth'] = Auth.from_kwargs(request.args.to_dict(), kwargs)
    user = kwargs['auth'].user

    # User must be logged in
    if user is None:
        raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)

    # User must have permissions
    if not target.has_permission(user, permission):
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    user = utils._get_user_by_auth(request)

    if user is None:
        raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)
    user_addon = user.get_addon(addon_name)

    node = _get_node_by_id(node_id)
    node_addon = node.get_addon(addon_name)

    _verify_permissions('WRITE', user, node)

    external_account = ExternalAccount.load(request.json['external_account_id'])

    if not user_addon.external_accounts.filter(id=external_account.id).exists():
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    try:
        node_addon.set_auth(external_account, user_addon.owner)
    except PermissionsError:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    node_addon.save()

    return {
        'result': BoxSerializer().serialize_settings(node_addon, auth.user),
        'message': 'Successfully imported access token from profile.',
    }


def box_folders_list(request):
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
