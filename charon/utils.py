import datetime
import logging

import jwe
import jwt
import requests
from django.utils import timezone

from . import models, settings

logger = logging.getLogger(__name__)
WATERBUTLER_JWE_KEY = jwe.kdf(
    settings.WATERBUTLER_JWE_SECRET.encode('utf-8'),
    settings.WATERBUTLER_JWE_SALT.encode('utf-8'),
)


# TODO: not sure i love accessing request outside of views
def _get_user(request):
    """Take django request object, extract auth properties, and get user identified
    by these properties
    """
    headers = {'Content-type': 'application/json'}
    if "Authorization" in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    cookies = request.COOKIES
    logger.error('¶¶¶¶ in utils._get_user headers:({}) cookies:({})'.format(dict(request.headers), cookies))
    resp = requests.get(
        'http://localhost:5000/api/v1/user/auth/',
        headers=headers,
        cookies=cookies,
    )
    logger.error('¶¶¶¶ in utils._get_user resp:({})'.format(resp))

    if resp.status_code != 200:
        logger.error(
            '¶¶¶¶ in utils._get_user got bad response data from osf: code:({}) '
            'content:({})'.format(resp.status_code, resp.content[0:500])
        )
        raise Exception('Couldnt get user properties for current user')

    resp_data = resp.json()
    logger.info('¶¶¶¶ in utils._get_user resp-data:({})'.format(resp_data))
    user_id = resp_data['data']['user_id']
    return {'id': user_id}


def _get_node_by_guid(request, node_id):
    """Take django request object, extract auth properties, and using these auth propertiesget user identified
    by these properties
    """
    logger.info('¶¶¶¶ in utils._get_node_by_guid headers:({}) cookies:({})'.format(
        dict(request.headers),
        request.COOKIES
    ))
    headers = {'Content-type': 'application/json'}
    if "Authorization" in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    cookies = request.COOKIES
    url = 'http://localhost:8000/v2/nodes/{}/'.format(node_id)
    logger.info('¶¶¶¶ in utils._get_node_by_guid url:({})'.format(url))
    resp = requests.get(
        url,
        headers=headers,
        cookies=cookies,
    )
    logger.info('¶¶¶¶ in utils._get_node_by_guid resp:({})'.format(resp))

    if resp.status_code != 200:
        logger.error(
            '¶¶¶¶ in utils._get_node_by_guid@ got bad response data from osf: '
            'code:({}) content:({})'.format(resp.status_code, resp.content[0:500])
        )
        raise Exception('Couldnt get node properties for node:({}) for current user'.format(node_id))

    resp_data = resp.json()
    logger.info('¶¶¶¶ in utils._get_node_by_guid resp-data:({})'.format(resp_data))

    props = {
        '_id': node_id,
        'title': resp_data['data']['attributes']['title'],
    }
    return props


def _lookup_creds_and_settings_for(user_id, node_props):
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


def _make_wb_auth_payload(user, creds_and_settings, callback_url):
    return {
        'payload': jwe.encrypt(
            jwt.encode(
                {
                    'exp': timezone.now()
                    + datetime.timedelta(seconds=settings.WATERBUTLER_JWT_EXPIRATION),
                    'data': {
                        'auth': _make_auth(
                            user
                        ),  # A waterbutler auth dict not an Auth object
                        'credentials': creds_and_settings['credentials'],
                        'settings': creds_and_settings['settings'],
                        'callback_url': callback_url,
                    },
                },
                settings.WATERBUTLER_JWT_SECRET,
                algorithm=settings.WATERBUTLER_JWT_ALGORITHM,
            ),
            WATERBUTLER_JWE_KEY,
        ).decode()
    }


def cas_get_login_url(url):
    # TODO: implement this!
    return url


class PermissionsError(Exception):
    """Raised if an action cannot be performed due to insufficient permissions"""

    pass


class AddonError(Exception):
    pass


class InvalidFolderError(AddonError):
    pass


class InvalidAuthError(AddonError):
    pass
