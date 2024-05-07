from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=True)
    vk_id = fields.Int(required=True)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)


class UsersListSchema(Schema):
    users = fields.Nested(UserSchema, many=True)