import abc
import logging

# from boxsdk import Client, OAuth2
# from boxsdk.exception import BoxAPIException

# from . import settings

logger = logging.getLogger(__name__)


# called in: serializer
# there is also a separate web_url_for() method called on a node object
# not sure what the context of this one is, need to look up
def web_url_for():
    return ''


# called in: serializer
# return link to static osf endpoint, specifically oauth_endpoint+box
def api_url_for():
    return ''


# may have been added for models inline attempt
def api_v2_url():
    return ''


class BoxSerializer(object):
    # explicit in addons.base.serializer.AddonSerializer
    __metaclass__ = abc.ABCMeta

    # abstract in addons.base.serializer.AddonSerializer
    # explicit in addons.box.serializer.BoxSerializer
    addon_short_name = 'box'

    # from addons.base.serializer.StorageAddonSerializer
    REQUIRED_URLS = (
        'auth',
        'importAuth',
        'folders',
        'files',
        'config',
        'deauthorize',
        'accounts',
    )

    # explicit in addons.base.serializer.AddonSerializer
    #   copy-over-comment: TODO take addon_node_settings, addon_user_settings
    def __init__(self, node_settings=None, user_settings=None):
        self.node_settings = node_settings
        self.user_settings = user_settings

    # abstract in addons.base.serializer.AddonSerializer
    # explicit in addons.base.serializer.OAuthAddonSerializer
    @property
    def credentials_owner(self):
        return self.user_settings.owner if self.user_settings else None

    # abstract in addons.base.serializer.AddonSerializer
    # explicit in addons.base.serializer.OAuthAddonSerializer
    @property
    def user_is_owner(self):
        if self.user_settings is None or self.node_settings is None:
            return False

        user_accounts = self.user_settings.external_accounts.all()
        return bool(
            self.node_settings.has_auth
            and self.node_settings.external_account in user_accounts
        )

    # abstract in addons.base.serializer.AddonSerializer
    # explicit in addons.base.serializer.OAuthAddonSerializer
    @property
    def serialized_urls(self):
        ret = self.addon_serialized_urls
        # Make sure developer returns set of needed urls
        for url in self.REQUIRED_URLS:
            msg = "addon_serialized_urls must include key '{0}'".format(url)
            assert url in ret, msg

        # ret.update({'settings': web_url_for('user_addons')})
        ret.update({'settings': 'https://localhost:5000/settings/addons/'})

        return ret

    # from addons.base.serializer.OAuthAddonSerializer
    @property
    def serialized_accounts(self):
        return [
            self.serialize_account(each)
            for each in self.user_settings.external_accounts.all()
        ]

    # from addons.base.serializer.OAuthAddonSerializer
    @property
    def serialized_user_settings(self):
        # inlined call addons.base.serializer.AddonSerializer.serialized_user_settings
        retval = {}
        retval['accounts'] = []
        if self.user_settings:
            retval['accounts'] = self.serialized_accounts

        return retval

    # explicit in addons.base.serializer.AddonSerializer
    @property
    def serialized_node_settings(self):
        result = {
            'nodeHasAuth': self.node_settings.has_auth,
            'userIsOwner': self.user_is_owner,
            'urls': self.serialized_urls,
        }

        if self.user_settings:
            result['userHasAuth'] = self.user_settings.has_auth
        else:
            result['userHasAuth'] = False

        if self.node_settings.has_auth:
            owner = self.credentials_owner
            if owner:
                result['urls']['owner'] = web_url_for(
                    'profile_view_id', uid=owner._primary_key
                )
                result['ownerName'] = owner.fullname
        return result

    # from addons.base.serializer.OAuthAddonSerializer
    def serialize_account(self, external_account):
        if external_account is None:
            return None
        return {
            'id': external_account._id,
            'provider_id': external_account.provider_id,
            'provider_name': external_account.provider_name,
            'provider_short_name': external_account.provider,
            'display_name': external_account.display_name,
            'profile_url': external_account.profile_url,
            'nodes': [
                self.serialize_granted_node(node)
                for node in self.user_settings.get_attached_nodes(
                    external_account=external_account
                )
            ],
        }

    # from addons.base.serializer.OAuthAddonSerializer
    # @collect_auth
    def serialize_granted_node(self, node, auth):
        # inline @collect_auth decorator (sortof)
        # this is weird, serialize_granted_node is called by serialize_account, which
        # is called by the serialized_accounts property. But why are we fucking w/ the
        # request this deep into the serializer?
        # serialized_accounts property is called by serialized_user_settings property
        # serialized_user_settings is called by addons.views.generic_views.account_list
        #
        # i think this is bogus, and an auth object should be passed in from outside
        #
        # request = None  # this is a flask request object, what is it doing here?
        # kwargs['auth'] = Auth.from_kwargs(request.args.to_dict(), kwargs)

        node_settings = node.get_addon(self.user_settings.oauth_provider.short_name)
        serializer = node_settings.serializer(node_settings=node_settings)
        urls = serializer.addon_serialized_urls
        urls['view'] = node.url

        return {
            'id': node._id,
            'title': node.title if node.can_view(auth) else None,
            'urls': urls,
        }

    # from addons.base.serializer.StorageAddonSerializer
    def serialize_settings(self, node_settings, current_user, client=None):
        # TODO: is this legit? Original code doesn't make sense
        self.node_settings = node_settings
        self.user_settings = current_user.get_addon('box')

        logger.info(
            '¢¢¢¢ BoxSerializer.serialize_settings: node_settings:({}) '
            'current_user:({}) client:({})'.format(node_settings, current_user, client)
        )

        self.node_settings = node_settings
        user_settings = node_settings.user_settings()
        current_user_settings = current_user.get_addon(self.addon_short_name)
        logger.info(
            '¢¢¢¢ BoxSerializer.serialize_settings: user_settings-from_node:({}) '
            'current_user_settings-from_user:({})'.format(
                user_settings, current_user_settings
            )
        )

        user_is_owner = (
            user_settings is not None and user_settings.owner() == current_user
        )
        logger.info(
            '¢¢¢¢ BoxSerializer.serialize_settings: '
            'user_is_owner:({})'.format(user_is_owner)
        )

        valid_credentials = self.credentials_are_valid(user_settings, client)
        logger.info(
            '¢¢¢¢ BoxSerializer.serialize_settings: '
            'valid_credentials:({})'.format(valid_credentials)
        )

        user_has_auth = (
            current_user_settings is not None and current_user_settings.has_auth
        )
        logger.info(
            '¢¢¢¢ BoxSerializer.serialize_settings: '
            'user_has_auth:({})'.format(user_has_auth)
        )

        # result = {
        #     'userIsOwner': user_is_owner,
        #     'nodeHasAuth': node_settings.has_auth,
        #     'urls': self.serialized_urls,
        #     'validCredentials': valid_credentials,
        #     'userHasAuth': current_user_settings is not None
        #     and current_user_settings.has_auth,
        # }
        result = {
            'userIsOwner': True,
            'nodeHasAuth': True,
            'urls': self.serialized_urls,
            'validCredentials': valid_credentials,
            'userHasAuth': True,
        }

        if node_settings.has_auth:
            # Add owner's profile URL
            # result['urls']['owner'] = web_url_for(
            #     'profile_view_id', uid=user_settings.owner._id
            # )
            result['urls']['owner'] = ('https://localhost:5000/profile/p4r65',)

            # result['ownerName'] = user_settings.owner.fullname
            result['ownerName'] = user_settings.owner().fullname

            # Show available folders
            if node_settings.folder_id is None:
                result['folder'] = {'name': None, 'path': None}
            elif valid_credentials:
                result['folder'] = self.serialized_folder(node_settings)
        return result

    # from addons.box.serializer.BoxSerializer
    def credentials_are_valid(self, user_settings, client):
        # from addons.box.models import Provider as Box  # Avoid circular import

        # if self.node_settings.has_auth:
        #     if Box(self.node_settings.external_account).refresh_oauth_key():
        #         return True

        # if user_settings:
        #     oauth = OAuth2(
        #         client_id=settings.BOX_KEY,
        #         client_secret=settings.BOX_SECRET,
        #         access_token=user_settings.external_accounts[0].oauth_key,
        #     )
        #     client = client or Client(oauth)
        #     try:
        #         client.user()
        #     except (BoxAPIException, IndexError):
        #         return False
        return True

    # from addons.box.serializer.BoxSerializer
    def serialized_folder(self, node_settings):
        # path = node_settings.fetch_full_folder_path()
        path = '/'
        return {
            'path': path,
            'name': path.replace('All Files', '', 1) if path != '/' else '/ (Full Box)',
        }

    # abstract in addons.base.serializer.AddonSerializer
    # explicit in addons.box.serializer.BoxSerializer
    @property
    def addon_serialized_urls(self):
        logger.error(
            '§§§§ addon_serialized_urls self.node_settings:({})'.format(
                self.node_settings
            )
        )
        node = self.node_settings.parent
        logger.error('§§§§ addon_serialized_urls node:({})'.format(node))
        # guid = node.guids.first()._id
        guid = node._id
        CHARON_ROOT = 'http://localhost:8011/charon'
        return {
            # 'auth': api_url_for('oauth_connect', service_name='box'),
            'auth': '{}/box/connect'.format(CHARON_ROOT),
            # 'importAuth': node.api_url_for('box_import_auth'),
            'importAuth': '{}/projects/{}/box/user_auth/'.format(CHARON_ROOT, guid),
            # 'files': node.web_url_for('collect_file_trees'),
            'files': 'https://localhost:5000/project/dve82/files/',
            # 'folders': node.api_url_for('box_folder_list'),
            'folders': '{}/projects/{}/box/folders/'.format(CHARON_ROOT, guid),
            # 'config': node.api_url_for('box_set_config'),
            'config': '{}/projects/{}/box/settings/'.format(CHARON_ROOT, guid),
            # 'configPUT': node.api_url_for('box_set_config'),
            'configPUT': '{}/projects/{}/box/settings/'.format(CHARON_ROOT, guid),
            # 'deauthorize': node.api_url_for('box_deauthorize_node'),
            'deauthorize': '{}/projects/{}/box/user_auth/'.format(CHARON_ROOT, guid),
            # 'accounts': node.api_url_for('box_account_list'),
            'accounts': '{}/settings/box/accounts/'.format(CHARON_ROOT),
        }
