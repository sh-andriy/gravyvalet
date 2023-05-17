import logging

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


def connect_box(request):
    logger.info('@@@ got request for connect_box')
    logger.info('@@@   request ib:({})'.format(request))

    auth_url_base = 'https://www.box.com/api/oauth2/authorize'
    callback_url = 'https://www.box.com/api/oauth2/token'

    # return HttpResponse("You tried to box, but box we didn't.")
    return redirect(callback_box)


def callback_box(request):
    logger.error('@@@ got request for callback_box')
    logger.error('@@@   request ib:({})'.format(request))
    template = loader.get_template('charon/callback.html')
    context = {}
    return HttpResponse(
        template.render(context, request),
        headers={'Cross-Origin-Opener-Policy': 'unsafe-none'},
    )


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
