# stub objects representing OSF models (mostly)
# some are helper classes


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
