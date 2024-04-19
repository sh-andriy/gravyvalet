import dataclasses


class Credentials:
    def asdict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessTokenCredentials(Credentials):
    access_token: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessKeySecretKeyCredentials(Credentials):
    access_key: str
    secret_key: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class UsernamePasswordCredentials(Credentials):
    username: str
    password: str
