from django.core.exceptions import ValidationError


def ensure_shared_client(oauth2_token_metadata):
    client_configs = set(
        account.external_service.oauth2_client_config
        for account in oauth2_token_metadata.linked_accounts
    )
    if len(client_configs) != 1:
        raise ValidationError(
            "OAuth2 Token Metadata is linked to mulitple services/clients"
        )
