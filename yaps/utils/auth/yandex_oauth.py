from typing import Optional

from yaps.settings import Config


class YandexOAuthUtil:
    @staticmethod
    def get_login_url(oauth_token: str) -> str:
        return f"{Config.YandexOAuth.login_url}?format=json&oauth_token={oauth_token}"

    @staticmethod
    def get_auth_url() -> Optional[str]:
        app_id = Config.YandexOAuth.app_id
        if not app_id:
            return None
        return f"{Config.YandexOAuth.auth_url}?response_type=token&client_id={app_id}"
