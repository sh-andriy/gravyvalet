from http import HTTPStatus

from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView

from addon_service.models import OAuth2TokenMetadata
from addon_service.oauth import utils as oauth_utils


class Oauth2CallbackView(APIView):
    """
    Handles oauth callbacks for the GV

    BOX format ` {'access_token': '<>', 'expires_in': 4030, 'restricted_to': [], 'refresh_token': '<>', 'token_type': 'bearer'}`
    """

    def get(self, request):
        state = request.GET.get("state")
        token_metadata = OAuth2TokenMetadata.objects.get(state_token=state)
        token_response_json = async_to_sync(oauth_utils.request_access_token)(
            token_metadata, authorization_code=request.GET["code"]
        )
        oauth_utils.update_from_token_endpoint_response(
            token_metadata, token_response_json
        )
        return Response(status_code=HTTPStatus.OK)
