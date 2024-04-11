from datetime import timedelta

from django.shortcuts import redirect
from django.utils import timezone
from rest_framework.views import APIView

from addon_service.models import (
    AuthorizedStorageAccount,
    ExternalCredentials,
    ExternalStorageService,
    OAuth2TokenMetadata,
    UserReference,
)


class OauthCallbackView(APIView):
    """
    Handles oauth callbacks for the GV
    """

    def get(self, request):
        state = request.GET.get("state")
        ess_id, user_uri = state.split(",")
        external_storage_service = ExternalStorageService.objects.get(id=ess_id)
        data = external_storage_service.get_oauth_data_from_callback(request)

        if isinstance(data["scope"], str):
            data["scope"] = [data["scope"]]

        OAuth2TokenMetadata.objects.update_or_create(
            state_token=state,
            defaults={
                "refresh_token": data["access_token"],
                "authorized_scopes": data["scope"],
                "access_token_expiration": timezone.now()
                + timedelta(seconds=data["expires_in"]),
            },
        )

        user_reference, _ = UserReference.objects.get_or_create(user_uri=user_uri)

        AuthorizedStorageAccount.objects.update_or_create(
            external_storage_service=external_storage_service,
            account_owner=user_reference,
            int_authorized_capabilities=[1],  # TODO: What should go here?
            defaults={
                "_credentials": ExternalCredentials.from_api_blob(data),
            },
        )

        return redirect(external_storage_service.api_base_url)
