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


# called in: utils
class Guid(object):
    def __init__(self):
        return


class Auth(object):
    def __init__(self):
        return

    # called in: views
    # have valid credentials been passed and a proper user identified?
    @property
    def logged_in(self):
        return False

    # called in: views
    # return User object representing the logged in user implied by the instatiation
    # creds
    def user(self):
        return {}


class User(object):
    def __init__(self):
        return

    # called in: views
    # returns a user_settings object for the addon
    def get_addon(self, addon_name):
        return {}


class Node(object):
    def __init__(self):
        # called in: serializer
        _id = None
        title = None

        return

    # called in: views
    # returns a node_settings object for the addon
    def get_addon(self, addon_name):
        return {}

    # called in: views
    # returns boolean indicateing if User object has `perm` access to the node
    def has_permission(self, user, perm):
        return False

    # called in: serializer
    # maybe a property or attribute?
    def url(self):
        return ''

    # called in: serializer
    # auth is an Auth object, but is created in a weird place
    def can_view(self, auth):
        return ''

    # called in: serializer
    # return API url for this node and given endpoint action
    def api_url_for(self, endpoint):
        return ''

    # called in: serializer
    # return API url for this node and given endpoint action
    def web_url_for(self, endpoint):
        return ''


# called in: views
class ExternalAccount(object):
    def __init__(self):
        # called in: serializer
        _id = None
        provider_id = None
        provider_name = None
        provider = None
        display_name = None
        profile_url = None

        return

    # called in: views
    @classmethod
    def load(cls, external_account_id):
        return cls(external_account_id)


class UserAddon(object):
    def __init__(self):
        # called in: serializer
        # oauth_provider has subproperty short_name
        oauth_provider = None

        return

    # called in: views, serializer
    # TODO: should be a property?
    # return a list or queryset like of external_accounts
    # .filter() is called on this in views
    # .all() is called on this in serializer
    def external_accounts(self):
        return []

    # called in: views, serializer
    # return User object related to this UserAddon, i think
    # serializer accesses ._primary_key attr on this object
    # serializer accesses .fullname attr on this object
    # TODO: property?
    def owner(self):
        return {}

    # called in: serializer
    # not sure if retval is a list or queryset
    def get_attached_nodes(self, external_account):
        return []

    # called in: serializer
    # property or attribute
    def has_auth(self):
        return False


class NodeAddon(object):
    def __init__(self):
        return

    # called in: views
    # set root folder id for nodeAddon
    def set_folder(self, folder_id, auth):
        return

    # called in: views
    # return list of folders under folder with id=folder_id
    def get_folders(self, folder_id):
        return []

    # called in: views
    # return string representing path of root folder
    # TODO: should be a property?
    def folder_path(self):
        return ''

    # called in: views
    # ???
    # external_account should be an ExternalAccount object
    # owner is a User object, i think
    def set_auth(external_account, owner):
        return {}

    # called in: views
    # save to store
    def save(self):
        return {}

    # called in: views
    # auth is an Auth object
    def deauthorize(self, auth):
        return

    # called in: serializer
    # property or attribute
    def has_auth(self):
        return False

    # called in: serializer
    # return linked ExternalAccount object
    # TODO: probably a property/attr
    def external_account(self):
        return {}

    # called in: serializer
    # either a property or attribute
    # returns UserAddon object related to this NodeAddon
    def user_settings(self):
        return {}

    # called in: serializer
    # returns "full" path for folder
    # not sure how this differs from folder_path
    def fetch_full_folder_path(self):
        return ''

    # called in: serializer
    # property or attribute
    # i'm guessing this just proxies to self.user_settings.owner
    def owner(self):
        return {}
