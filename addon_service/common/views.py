from django.shortcuts import redirect
from rest_framework.views import View

from addon_service.models import (
    AuthorizedStorageAccount,
    ExternalCredentials,
    ExternalStorageService,
    OAuth2TokenMetadata,
)


class OauthCallbackView(View):
    """
    Handles oauth callbacks for the GV
    """

    authentication_classes = ()  # TODO: many options but safest just to whitelist providers I think
    permission_classes = ()

    def get(self, request):
        state = request.GET.get("state")
        external_storage_service = ExternalStorageService.objects.get(id=state)
        data = external_storage_service.get_oauth_data_from_callback(request)

        external_credentials = ExternalCredentials.objects.create(credentials_blob=data)

        OAuth2TokenMetadata.objects.create(
            token_source=external_credentials,
            state_token=state,
            refresh_token=data["refresh_token"],
            authorized_scopes=data["scopes"],
            auth_token_expiration=data["auth_token_expiration"],
        )

        AuthorizedStorageAccount.objects.create(
            external_storage_service=external_storage_service,
            account_owner=request.user,
            _credentials=data,
        )

        return redirect(state)
