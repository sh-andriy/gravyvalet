import dataclasses
import typing

from addon_toolkit.json_arguments import json_for_dataclass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Credentials(typing.Protocol):
    def asdict(self):
        return json_for_dataclass(self)

    def iter_headers(self) -> typing.Iterator[tuple[str, str]]:
        yield from ()


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessTokenCredentials(Credentials):
    access_token: str

    def iter_headers(self):
        yield ("Authorization", f"Bearer {self.access_token}")


@dataclasses.dataclass(frozen=True, kw_only=True)
class AccessKeySecretKeyCredentials(Credentials):
    access_key: str
    secret_key: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class UsernamePasswordCredentials(Credentials):
    username: str
    password: str
