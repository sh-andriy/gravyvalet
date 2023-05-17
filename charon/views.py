import json
import logging

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

# from django.shortcuts import render

# Create your views here.


logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse(
        "Hello, world. Welcome to the continental, rated two stars on tripadvisor."
    )


def _get_user_id(request):
    headers = {'Content-type': 'application/json'}
    if "Authorization" in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    cookies = request.COOKIES
    resp = requests.get(
        'http://localhost:5000/api/v1/user/auth/',
        headers=headers,
        cookies=cookies,
    )

    user_id = None
    if resp.status_code == 200:
        # raw_data = resp.json
        # logger.error('@@@ got raw response data from osf: {}'.format(raw_data))
        resp_data = resp.json()
        logger.error('@@@ got response data from osf: {}'.format(resp_data))
        user_id = resp_data['data']['user_id']
    else:
        logger.error(
            '@@@ got bad response data from osf: code:({}) '
            'content:({})'.format(resp.status_code, resp.content)
        )

    return user_id


def _lookup_creds_and_settings_for(user_id, node_id, args):
    credentials, settings = None, None
    return {
        'credentials': credentials,
        'settings': settings,
    }


def _make_auth(user):
    if user is not None:
        return {
            'id': user._id,
            'email': '{}@osf.io'.format(user._id),
            'name': user.fullname,
        }
    return {}


def _make_osf_callback_url(node_props):
    callback_url = settings.OSF_CALLBACK_BASE

    # _absolute=True,
    # _internal=True

    if node_props.is_registration:
        callback_url += 'registration_callbacks'
    else:
        callback_url += 'create_waterbutler_log'

    return callback_url


def connect_box(request):
    logger.error('@@@ got request for connect_box')
    logger.error('@@@   request ib:({})'.format(request))

    user = _get_user(request)

    auth_url_base = 'https://www.box.com/api/oauth2/authorize'
    callback_url = 'https://www.box.com/api/oauth2/token'

    # return HttpResponse("You tried to box, but box we didn't.")
    response = redirect(callback_box)
    response['Cross-Origin-Opener-Policy'] = 'unsafe-none'
    return response


def callback_box(request):
    logger.error('@@@ got request for callback_box')
    logger.error('@@@   request ib:({})'.format(request))
    logger.error('@@@   headers are:({})'.format(request.headers))
    template = loader.get_template('charon/callback.html')
    user = _get_user(request)
    context = {'user_id': user['id'] if user else '*no user id*'}
    return HttpResponse(
        template.render(context, request),
        headers={'Cross-Origin-Opener-Policy': 'unsafe-none'},
    )


def get_credentials(request):
    logger.error('@@@ got request for get_credentials')

    user_id = _get_user_id(request)
    # check_access(node, auth, action, cas_resp)
    # provider_settings = None
    # if hasattr(node, 'get_addon'):
    #     provider_settings = node.get_addon(provider_name)
    #     if not provider_settings:
    #         raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    node_props = _get_node_properties(node_id)
    creds_and_settings = _lookup_creds_and_settings_for(user_id, node_id, args)

    callback_url = _make_api_url_for(node_props)

    return {
        'payload': jwe.encrypt(
            jwt.encode(
                {
                    'exp': timezone.now()
                    + datetime.timedelta(seconds=settings.WATERBUTLER_JWT_EXPIRATION),
                    'data': {
                        'auth': make_auth(
                            auth.user
                        ),  # A waterbutler auth dict not an Auth object
                        'credentials': credentials,
                        'settings': waterbutler_settings,
                        'callback_url': callback_url,
                    },
                },
                settings.WATERBUTLER_JWT_SECRET,
                algorithm=settings.WATERBUTLER_JWT_ALGORITHM,
            ),
            WATERBUTLER_JWE_KEY,
        ).decode()
    }


# from website.oauth.views
# @must_be_logged_in
# def oauth_connect(service_name, auth):
#     service = get_service(service_name)

#     return redirect(service.auth_url)

# from website.oauth.views
# @must_be_logged_in
# def oauth_callback(service_name, auth):
#     user = auth.user
#     provider = get_service(service_name)

#     # Retrieve permanent credentials from provider
#     if not provider.auth_callback(user=user):
#         return {}

#     if provider.account and not user.external_accounts.filter(id=provider.account.id).exists():
#         user.external_accounts.add(provider.account)
#         user.save()

#     oauth_complete.send(provider, account=provider.account, user=user)

#     return {}

# from addons.models.base
# @oauth_complete.connect
# def oauth_complete(provider, account, user):
#     if not user or not account:
#         return
#     user.add_addon(account.provider)
#     user.save()


# @collect_auth
# def get_auth(auth, **kwargs):
#     cas_resp = None
#     # Central Authentication Server OAuth Bearer Token
#     authorization = request.headers.get('Authorization')
#     if authorization and authorization.startswith('Bearer '):
#         client = cas.get_client()
#         try:
#             access_token = cas.parse_auth_header(authorization)
#             cas_resp = client.profile(access_token)
#         except cas.CasError as err:
#             sentry.log_exception()
#             # NOTE: We assume that the request is an AJAX request
#             return json_renderer(err)
#         if cas_resp.authenticated and not getattr(auth, 'user'):
#             auth.user = OSFUser.load(cas_resp.user)

#     try:
#         data = jwt.decode(
#             jwe.decrypt(request.args.get('payload', '').encode('utf-8'), WATERBUTLER_JWE_KEY),
#             settings.WATERBUTLER_JWT_SECRET,
#             options={'require_exp': True},
#             algorithm=settings.WATERBUTLER_JWT_ALGORITHM
#         )['data']
#     except (jwt.InvalidTokenError, KeyError) as err:
#         sentry.log_message(str(err))
#         raise HTTPError(http_status.HTTP_403_FORBIDDEN)

#     if not auth.user:
#         auth.user = OSFUser.from_cookie(data.get('cookie', ''))

#     try:
#         action = data['action']
#         node_id = data['nid']
#         provider_name = data['provider']
#     except KeyError:
#         raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

#     node = AbstractNode.load(node_id) or Preprint.load(node_id)
#     if node and node.is_deleted:
#         raise HTTPError(http_status.HTTP_410_GONE)
#     elif not node:
#         raise HTTPError(http_status.HTTP_404_NOT_FOUND)

#     check_access(node, auth, action, cas_resp)
#     provider_settings = None
#     if hasattr(node, 'get_addon'):
#         provider_settings = node.get_addon(provider_name)
#         if not provider_settings:
#             raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

#     path = data.get('path')
#     credentials = None
#     waterbutler_settings = None
#     fileversion = None
#     if provider_name == 'osfstorage':
#         if path:
#             file_id = path.strip('/')
#             # check to see if this is a file or a folder
#             filenode = OsfStorageFileNode.load(path.strip('/'))
#             if filenode and filenode.is_file:
#                 # default to most recent version if none is provided in the response
#                 version = int(data['version']) if data.get('version') else filenode.versions.count()
#                 try:
#                     fileversion = FileVersion.objects.filter(
#                         basefilenode___id=file_id,
#                         identifier=version
#                     ).select_related('region').get()
#                 except FileVersion.DoesNotExist:
#                     raise HTTPError(http_status.HTTP_400_BAD_REQUEST)
#                 if auth.user:
#                     # mark fileversion as seen
#                     FileVersionUserMetadata.objects.get_or_create(user=auth.user, file_version=fileversion)
#                 if not node.is_contributor_or_group_member(auth.user):
#                     from_mfr = download_is_from_mfr(request, payload=data)
#                     # version index is 0 based
#                     version_index = version - 1
#                     if action == 'render':
#                         enqueue_update_analytics(node, filenode, version_index, 'view')
#                     elif action == 'download' and not from_mfr:
#                         enqueue_update_analytics(node, filenode, version_index, 'download')
#                     if waffle.switch_is_active(features.ELASTICSEARCH_METRICS):
#                         if isinstance(node, Preprint):
#                             metric_class = get_metric_class_for_action(action, from_mfr=from_mfr)
#                             if metric_class:
#                                 try:
#                                     metric_class.record_for_preprint(
#                                         preprint=node,
#                                         user=auth.user,
#                                         version=fileversion.identifier if fileversion else None,
#                                         path=path,
#                                     )
#                                 except es_exceptions.ConnectionError:
#                                     log_exception()
#         if fileversion and provider_settings:
#             region = fileversion.region
#             credentials = region.waterbutler_credentials
#             waterbutler_settings = fileversion.serialize_waterbutler_settings(
#                 node_id=provider_settings.owner._id,
#                 root_id=provider_settings.root_node._id,
#             )
#     # If they haven't been set by version region, use the NodeSettings or Preprint directly
#     if not (credentials and waterbutler_settings):
#         credentials = node.serialize_waterbutler_credentials(provider_name)
#         waterbutler_settings = node.serialize_waterbutler_settings(provider_name)

#     if isinstance(credentials.get('token'), bytes):
#         credentials['token'] = credentials.get('token').decode()

#     return {'payload': jwe.encrypt(jwt.encode({
#         'exp': timezone.now() + datetime.timedelta(seconds=settings.WATERBUTLER_JWT_EXPIRATION),
#         'data': {
#             'auth': make_auth(auth.user),  # A waterbutler auth dict not an Auth object
#             'credentials': credentials,
#             'settings': waterbutler_settings,
#             'callback_url': node.api_url_for(
#                 ('create_waterbutler_log' if not getattr(node, 'is_registration', False) else 'registration_callbacks'),
#                 _absolute=True,
#                 _internal=True
#             )
#         }
#     }, settings.WATERBUTLER_JWT_SECRET, algorithm=settings.WATERBUTLER_JWT_ALGORITHM), WATERBUTLER_JWE_KEY).decode()}
