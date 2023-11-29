from marshmallow import Schema, fields
from utils import OperationTypeEnum


class AccessSchema(Schema):
    class Meta:
        fields = ('id', 'resource')


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    surname = fields.Str()
    accesses = fields.Nested(AccessSchema, many=True)


class AccessChangeHistorySchema(Schema):
    user_id = fields.Str()
    created_at = fields.DateTime()
    changes = fields.Str()
    operation = fields.Enum(OperationTypeEnum)


class ChangeAccessSchema(Schema):
    resource = fields.String(required=True)


class CreateUserSchema(Schema):
    name = fields.String(required=True)
    surname = fields.String(required=True)
    resource = fields.String(required=True)
