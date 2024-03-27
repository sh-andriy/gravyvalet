from enum import Enum


class CredentialsFormats(Enum):
    UNSPECIFIED = 0
    OAUTH2 = 1
    S3_LIKE = 2
    USER_PASS = 3
    USER_PASS_HOST = 4
