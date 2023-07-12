# stub objects representing OSF models (mostly)
# some are helper classes

import json
import logging

logger = logging.getLogger(__name__)

DB = None
DB_ROOT = 'db'
with open('{}/charon.json'.format(DB_ROOT)) as json_file:
    DB = json.load(json_file)


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
    def __init__(self, _id):
        self._id = _id
        self._props = DB['users'].get(_id, None)
        if self._props is not None:
            self.fullname = self._props['fullname']
            self._our_external_accounts = [
                ExternalAccount(_id=x) for x in self._props['external_accounts']
            ]
        return

    # called in: views
    # returns a user_settings object for the addon
    def get_addon(self, addon_name):
        return UserAddon(self, addon_name)

    @property
    def external_accounts(self):
        return ExternalAccountProxy(self._our_external_accounts)


class Node(object):
    def __init__(self, _id, title):
        # called in: serializer
        self._id = _id
        self._props = DB['nodes'].get(_id, None)
        self.title = title
        return

    # called in: views
    # returns a node_settings object for the addon
    def get_addon(self, addon_name):
        return NodeAddon(self, addon_name)

    # called in: views
    # returns boolean indicateing if User object has `perm` access to the node
    def has_permission(self, user, perm):
        if DB['permissions'].get(self._id, False):
            return DB['permissions'][self._id].get(user._id, False)

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
    def __init__(self, _id):
        # called in: serializer
        self._id = _id
        self._props = DB['external_accounts'].get(_id, None)

        if self._props is not None:
            self.provider_id = self._props['provider_id']
            self.provider_name = self._props['provider_name']
            self.provider = self._props['provider']
            self.display_name = self._props['display_name']
            self.profile_url = self._props['profile_url']

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
    def __init__(self, parent, addon_name):
        logger.error(
            '$$$ UserAddon.__init__ -- parent:({})  addon_name:({})'.format(
                parent, addon_name
            )
        )

        self.parent = parent
        self.addon_name = addon_name

        if self.parent is not None:
            user_addons_props = DB['user_addons'].get(parent._id, None)
            self._props = user_addons_props.get(addon_name, None)
            self.fake_name = self._props.get('fake_name', None)
            self.external_accounts = self.parent.external_accounts

            # called in: serializer
            # oauth_provider has subproperty short_name
            self.oauth_provider = self._props['oauth_provider']

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
    def __init__(self, parent, addon_name):
        logger.error(
            '$$$ NodeAddon.__init__ -- parent:({})  addon_name:({})'.format(
                parent, addon_name
            )
        )

        self.parent = parent
        self.addon_name = addon_name

        if self.parent is not None:
            node_addons_props = DB['node_addons'].get(parent._id, None)
            self._props = node_addons_props.get(addon_name, None)
            self.fake_name = self._props.get('fake_name', None)
            self.folder_id = self._props.get('folder_id', None)

        return

    # called in: views
    # set root folder id for nodeAddon
    def set_folder(self, folder_id, auth):
        self.folder_id = folder_id
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
        # user_settings = owner.get_addon(self.addon_name)
        # self.user_settings = user_settings
        return

    # called in: views
    # save to store
    def save(self):
        # save current state of DB?
        with open('{}/charon.json'.format(DB_ROOT), "w") as json_file:
            json.dump(DB, json_file)
        return

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
        return User('p4r65').get_addon(self.addon_name)

    # called in: serializer
    # returns "full" path for folder
    # not sure how this differs from folder_path
    def fetch_full_folder_path(self):
        return ''

    # called in: serializer
    # property or attribute
    # i'm guessing this just proxies to self.user_settings.owner
    def owner(self):
        return self.user_settings().owner
