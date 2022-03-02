from marshmallow import Schema
from marshmallow.fields import Int, Str


class AuthSchema(Schema):
    auth_token = Str(required=True, description="Токен доступа")
    email = Str(required=True, description="Email клиента")
    expires_at = Int(
        required=True, description="Временная метка истечения жизни сессии"
    )


class TokenSchema(Schema):
    token = Str(data_key="access_token", required=True)
