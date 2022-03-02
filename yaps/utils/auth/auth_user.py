from typing import NamedTuple


class AuthUser(NamedTuple):
    email: str
    access_token: str
