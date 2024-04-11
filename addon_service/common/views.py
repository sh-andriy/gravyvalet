from datetime import timedelta

from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.views import APIView

from addon_service.models import OAuth2TokenMetadata
from addon_service.common.oauth import get_oauth_token_data_from_code


class OauthCallbackView(APIView):
    """
    Handles oauth callbacks for the GV

    BOX format ` {'access_token': '<>', 'expires_in': 4030, 'restricted_to': [], 'refresh_token': '<>', 'token_type': 'bearer'}`
    """

    def get(self, request):
        state = request.GET.get("state")
        token_metadata = OAuth2TokenMetadata.objects.get(state_token=state)
        asa = token_metadata.authorized_storage_accounts.first()
        data = get_oauth_token_data_from_code(
            exernal_storage_service=asa.external_storage_service,
            code=request.GET['code']
        )

        token_metadata.refresh_token = data.get("refresh_token") or data["access_token"]
        token_metadata.access_token_expiration = timezone.now() + timedelta(seconds=data["expires_in"])

        token_metadata.state_token = None
        token_metadata.save()
        asa.set_credentials(data)

        return redirect('/')
