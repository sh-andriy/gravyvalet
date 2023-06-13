# stub objects representing OSF models (mostly)
# some are helper classes

import logging

logger = logging.getLogger(__name__)


# called in: utils
class Guid(object):
    def __init__(self):
        # called in views
        referent = None

        return

    # called in views
    @classmethod
    def load(cls, project_guid):
        return cls(project_guid)


class Auth(object):
    def __init__(self, user):
        # called in: views
        # return User object representing the logged in user implied by the instatiation
        # creds
        self.user = user
        return

    # called in: views
    # have valid credentials been passed and a proper user identified?
    @property
    def logged_in(self):
        return self.user is not None


class User(object):
    OTHER_PROPERTIES = {
        'mst3k': {},
        'fbi4u': {},
        'p4r65': {
            'user_addon': {
                'box': {'fake_name': 'meow'},
            },
            'external_accounts': [
                {
                    '_id': 'alpha',
                    'provider_id': 'plopsome-alpha',
                    'provider_name': 'borfhome-alpha',
                    'provider': 'crechdolg-alpha',
                    'display_name': 'dumpfust-alpha',
                    'profile_url': 'enchhort-alpha',
                },
                {
                    '_id': 'beta',
                    'provider_id': 'plopsome-beta',
                    'provider_name': 'borfhome-beta',
                    'provider': 'crechdolg-beta',
                    'display_name': 'dumpfust-beta',
                    'profile_url': 'enchhort-beta',
                },
            ],
        },
    }


    def __init__(self, user_id):
        self.user_id = user_id
        self._props = self.OTHER_PROPERTIES.get(user_id, None)
        self._our_external_accounts = [ExternalAccount(props=x) for x in self._props['external_accounts']]
        return

    # called in: views
    # returns a user_settings object for the addon
    def get_addon(self, addon_name):
        if self._props is not None:
            user_addon = UserAddon(self, self._props['user_addon'][addon_name])
            return user_addon
        return None

    @property
    def external_accounts(self):
        return ExternalAccountProxy(self._our_external_accounts)


class Node(object):
    OTHER_PROPERTIES = {
        'mst3k': {},
        'fbi4u': {},
        'dve82': {
            'node_addon': {
                'box': {'fake_name': 'meow'},
            },
        },
    }

    def __init__(self, _id, title):
        # called in: serializer
        self._id = _id
        self._props = self.OTHER_PROPERTIES.get(_id, None)
        self.title = title
        return

    # called in: views
    # returns a node_settings object for the addon
    def get_addon(self, addon_name):
        if self._props is not None:
            node_addon = NodeAddon(self, self._props['node_addon'][addon_name])
            return node_addon
        return None

    # called in: views
    # returns boolean indicateing if User object has `perm` access to the node
    def has_permission(self, user, perm):
        PERMISSION_MAP = {
            'dve82': {
                'p4r65': True,
            }
        }

        if PERMISSION_MAP.get(self._id, False):
            if PERMISSION_MAP[self._id].get(user.user_id, False):
                return PERMISSION_MAP[self._id][user.user_id]

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
    def __init__(self, props):
        # called in: serializer
        self._id = None
        self.provider_id = None
        self.provider_name = None
        self.provider = None
        self.display_name = None
        self.profile_url = None

        return

    # called in: views
    @classmethod
    def load(cls, external_account_id):
        return cls(external_account_id)


class ExternalAccountProxy(object):
    def __init__(self, external_accounts):
        self.external_accounts = external_accounts

    def all(self):
        return self.external_accounts

    def filter(self, _id):
        filtered = [e for e in self.external_accounts if e._id == _id]
        return ExternalAccountProxy(filtered)

    def exists(self):
        return len(self.external_accounts) > 0


class UserAddon(object):
    OTHER_PROPERTIES = {
        'meow': {
            'oauth_provider': {'short_name': 'box'},
        },
        'quack': {},
        'woof': {},
    }


    def __init__(self, parent, props):
        logger.error('$$$ qwa?? parent:({})  props:({})'.format(parent, props))

        self.parent = parent
        self.fake_name = props.get('fake_name', None)
        self.external_accounts = self.parent.external_accounts

        if not self.fake_name:
            raise Exception('Dunno how to incept this UserAddon wo a fake_name')

        our_props = self.OTHER_PROPERTIES.get(self.fake_name, None)
        if not our_props:
            raise Exception('Dunno how to incept this UserAddon w/ a bad fake_name')

        # called in: serializer
        # oauth_provider has subproperty short_name
        self.oauth_provider = our_props['oauth_provider']

        return

    # called in: views, serializer
    # TODO: should be a property?
    #   no, calls .external_accounts on user
    # return a list or queryset like of external_accounts
    # .filter() is called on this in views
    # .all() is called on this in serializer
    # def external_accounts(self):
    #     return self.parent.external_accounts

    # called in: views, serializer
    # return User object related to this UserAddon, i think
    # serializer accesses ._primary_key attr on this object
    # serializer accesses .fullname attr on this object
    # TODO: property?
    def owner(self):
        return self.parent

    # called in: serializer
    # not sure if retval is a list or queryset
    def get_attached_nodes(self, external_account):
        return []

    # called in: serializer
    # property or attribute
    def has_auth(self):
        return False


class NodeAddon(object):
    def __init__(self, parent, props):
        logger.error('$$$ NodeAddon parent:({})  props:({})'.format(parent, props))

        self.parent = parent
        self.fake_name = props.get('fake_name', None)
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
    def set_auth(self, external_account, owner):
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
