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
            'content:({})'.format(resp.status_code, resp.content[0:500])
        )
        logger.error('@@@ DONT EVER DO THIS!, back this out')
        user_id = 'p4r65'

    return {'id': user_id}


def _get_node_by_guid(node_id):
    NODE_PROPERTIES = {
        'dve82': {
            '_id': 'dve82',
            'title': 'Provider - S3',
        },
    }
    props = NODE_PROPERTIES.get(node_id, None)
    if props is None:
        return None
    node = models.Node(props['_id'], props['title'])
    return node


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
