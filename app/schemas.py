from flask import current_app
from app import ma
from app.models import User
from app.models import Post
from app.models import Like
from app.utils.string_manipulation import truncate_string


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class LikeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Like

    post_id = ma.auto_field()
    user = ma.Nested(UserSchema)


class OverallLikeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Like

    latest_likes = ma.Function(
        lambda likes: LikeSchema(many=True).dump(likes.limit(3).all())
    )
    total = ma.Function(lambda likes: likes.count())


class PostListSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
    
    id = ma.auto_field()
    title = ma.auto_field()
    body = ma.Function(
        lambda post: truncate_string(post.body, current_app.config["BODY_OVERVIEW_LENGTH"])
    )
    created_at = ma.auto_field()
    author = ma.Nested(UserSchema)
    likes = ma.Nested(OverallLikeSchema)


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post

    id = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()
    created_at = ma.auto_field()
    author = ma.Nested(UserSchema)
    likes = ma.Nested(OverallLikeSchema)
