from .enums import CredentialsSources


def deserialize_credentials(credentials_blob, credentials_source):
    match credentials_source:
        case CredentialsSources.OSF_API:
            return dict(credentials_blob)
        case CredentialsSources.OAUTH2_TOKEN_ENDPOINT:
            return {"access_token": credentials_blob["access_token"]}
