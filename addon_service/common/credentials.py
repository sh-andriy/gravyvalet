from enum import Enum

class CredentialsFormats(Enum):
    UNSPECIFIED = 0
    OAUTH = 1
    S3_LIKE = 2
    USER_PASS = 3
    USER_PASS_HOST = 4

    @property
    def required_fields(self):
        # TODO: This is maybe overly-coupled with the models...
        match self:
            case CredentialsFormats.OAUTH:
                return {'oauth_access_token'}
            case CredentialsFormats.S3_Like:
                return {'access_key', 'secret_key'}
            case CredentialsFormats.USER_PASS:
                return {'user_name', 'pwd'}
            case CredentialsFormats.USER_PASS_HOST:
                return {'user_name', 'pwd', 'service_host'}
        raise ValueError(f'{self.name} has no specified required credentials fields')
