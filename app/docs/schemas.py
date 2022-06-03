from flasgger import Schema
from flasgger import fields


class UserResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GeneratedTokensResponseSchema(Schema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)


class LikeResponseSchema(Schema):
    post_id = fields.Int()
    user = fields.Nested(UserResponseSchema)


class OverallLikeResponseSchema(Schema):
    latest_likes = fields.Nested(UserResponseSchema, many=True)
    total = fields.Int()


class PostResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    body = fields.Str()
    created_at = fields.DateTime()
    author = fields.Nested(UserResponseSchema)
    likes = fields.Nested(OverallLikeResponseSchema)


class FbUserProfileResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    phone = fields.Str()
    posts = fields.Nested(PostResponseSchema, many=True)


class GgUserProfileResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    occupation = fields.Str()
    posts = fields.Nested(PostResponseSchema, many=True)
