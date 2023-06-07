import datetime
import logging

import jwe
import jwt
import requests
from django.utils import timezone

from . import settings

logger = logging.getLogger(__name__)
WATERBUTLER_JWE_KEY = jwe.kdf(
    settings.WATERBUTLER_JWE_SECRET.encode('utf-8'),
    settings.WATERBUTLER_JWE_SALT.encode('utf-8'),
)


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
            'content:({})'.format(resp.status_code, resp.content)
        )

    return {'id': user_id}


def _get_node_properties(node_id):
    return {}


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


def _get_node_by_guid(project_guid):
    return getattr(Guid.load(project_guid), 'referent', None)


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


# stub objects representing OSF models (mostly)
# some are helper classes


class Guid(object):
    def __init__(self):
        return


class Auth(object):
    def __init__(self):
        return

    # have valid credentials been passed and a proper user identified?
    @property
    def logged_in(self):
        return False

    # return User object representing the logged in user implied by the instatiation
    # creds
    def user(self):
        return {}


class User(object):
    def __init__(self):
        return

    # returns a user_settings object for the addon
    def get_addon(self, addon_name):
        return {}


class Node(object):
    def __init__(self):
        return

    # returns a node_settings object for the addon
    def get_addon(self, addon_name):
        return {}

    # returns boolean indicateing if User object has `perm` access to the node
    def has_permission(self, user, perm):
        return False


class ExternalAccount(object):
    def __init__(self):
        return

    @classmethod
    def load(cls, external_account_id):
        return cls(external_account_id)


class UserAddon(object):
    def __init__(self):
        return

    # TODO: should be a property?
    # return a list or queryset like of external_accounts
    # .filter() is called on this
    def external_accounts(self):
        return []

    # return User object related to this UserAddon, i think
    # TODO: property?
    def owner(self):
        return {}


class NodeAddon(object):
    def __init__(self):
        return

    # set root folder id for nodeAddon
    def set_folder(self, folder_id, auth):
        return

    # return list of folders under folder with id=folder_id
    def get_folders(self, folder_id):
        return []

    # return string representing path of root folder
    # TODO: should be a property?
    def folder_path(self):
        return ''

    # ???
    # external_account should be an ExternalAccount object
    # owner is a User object, i think
    def set_auth(external_account, owner):
        return {}

    # save to store
    def save(self):
        return {}

    # auth is an Auth object
    def deauthorize(self, auth):
        return
