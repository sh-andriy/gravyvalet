import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessTokenCredentials:
    access_token: str
    expires_in: str
    token_type: str
    restricted_to: str
    scope: str = None
    refresh_token: str = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessKeySecretKeyCredentials:
    access_key: str
    secret_key: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class UsernamePasswordCredentials:
    username: str
    password: str
