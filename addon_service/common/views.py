from django.shortcuts import redirect
from rest_framework.views import APIView

from addon_service.models import OAuth2TokenMetadata
from addon_service.oauth import utils as oauth_utils


class OauthCallbackView(APIView):
    """
    Handles oauth callbacks for the GV

    BOX format ` {'access_token': '<>', 'expires_in': 4030, 'restricted_to': [], 'refresh_token': '<>', 'token_type': 'bearer'}`
    """

    def get(self, request):
        state = request.GET.get("state")
        token_metadata = OAuth2TokenMetadata.objects.get(state_token=state)
        account = token_metadata.authorized_storage_accounts.first()
        oauth_utils.perform_oauth2_token_exchange(
            account, authorization_code=request.GET["code"]
        )
        return redirect("/")
