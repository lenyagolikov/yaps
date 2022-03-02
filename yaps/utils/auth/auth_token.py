import hashlib
import re
from typing import Optional, Any

from aiohttp import web

from yaps.settings import Config


class AuthUtils:

    token_re: Any = re.compile(Config.Auth.token_type + r" (.+)")

    @classmethod
    def extract_auth_token(cls, request: web.Request) -> Optional[str]:
        header_val = request.headers.get(Config.Auth.auth_header)
        if not header_val:
            return None
        res = cls.token_re.findall(header_val)
        return res[0] if res else None

    @classmethod
    def gen_auth_token(cls, user_email: str, access_token: str) -> str:
        encoded_key = (user_email + access_token).encode()
        return hashlib.sha256(encoded_key).hexdigest()
