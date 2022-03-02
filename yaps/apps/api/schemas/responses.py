from marshmallow import Schema
from marshmallow.fields import Str


class BadRequestSchema(Schema):
    message = Str(required=True, description="bad-parameters")


class NotFoundSchema(Schema):
    message = Str(required=True, description="not-found")


class UnauthorizedSchema(Schema):
    message = Str(required=True, description="unauthorized")
