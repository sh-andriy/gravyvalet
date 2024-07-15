from enum import (
    Enum,
    unique,
)

from addon_toolkit import credentials


@unique
class CredentialsFormats(Enum):
    UNSPECIFIED = 0
    OAUTH2 = 1
    ACCESS_KEY_SECRET_KEY = 2
    USERNAME_PASSWORD = 3
    PERSONAL_ACCESS_TOKEN = 4
    OAUTH1A = 5

    @property
    def dataclass(self):
        match self:
            case CredentialsFormats.OAUTH2:
                return credentials.AccessTokenCredentials
            case CredentialsFormats.OAUTH1A:
                return credentials.OAuth1Credentials
            case CredentialsFormats.ACCESS_KEY_SECRET_KEY:
                return credentials.AccessKeySecretKeyCredentials
            case CredentialsFormats.PERSONAL_ACCESS_TOKEN:
                return credentials.AccessTokenCredentials
            case CredentialsFormats.USERNAME_PASSWORD:
                return credentials.UsernamePasswordCredentials
        raise ValueError(f"No dataclass support for credentials type {self.name}")

    @property
    def is_direct_from_user(self):
        return self in {
            CredentialsFormats.ACCESS_KEY_SECRET_KEY,
            CredentialsFormats.USERNAME_PASSWORD,
            CredentialsFormats.PERSONAL_ACCESS_TOKEN,
        }
