
# ========== CODE BEING REIMPLEMENTED ==========

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

# from: website.project.decorators
# def must_have_addon(addon_name, model):
#     """Decorator factory that ensures that a given addon has been added to
#     the target node. The decorated function will throw a 404 if the required
#     addon is not found. Must be applied after a decorator that adds `node` and
#     `project` to the target function's keyword arguments, such as
#     `must_be_contributor.

#     :param str addon_name: Name of addon
#     :param str model: Name of model
#     :returns: Decorator function

#     """
#     def wrapper(func):

#         @functools.wraps(func)
#         @collect_auth
#         def wrapped(*args, **kwargs):
#             if model == 'node':
#                 _inject_nodes(kwargs)
#                 owner = kwargs['node']
#             elif model == 'user':
#                 auth = kwargs.get('auth')
#                 owner = auth.user if auth else None
#                 if owner is None:
#                     raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)
#             else:
#                 raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

#             addon = owner.get_addon(addon_name)
#             if addon is None:
#                 raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

#             kwargs['{0}_addon'.format(model)] = addon

#             return func(*args, **kwargs)

#         return wrapped

#     return wrapper
