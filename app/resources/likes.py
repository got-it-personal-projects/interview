from flask import request
from flask import current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from app import db
from app.models import Like
from app.models import Post
from app.schemas import LikeSchema
from app.utils.errors import error_response
from app.utils import http_responses


class PostLikeList(Resource):
    @jwt_required()
    def get(self, post_id):
        """
        Get list of a post's likes
        ---
        tags:
          - likes
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
            required: true
          - in: path
            name: post_id
            required: true
            type: string
        responses:
          200:
            description: List of a post's likes
            schema:
              type: array
              items:
                $ref: '#/definitions/LikeResponse'
          401:
            description: Invalid token
          404:
            description: Post not found
        """

        post = Post.query.filter_by(id=post_id).first()

        if post is None:
            return http_responses.not_found(error_response(f"Post with id {post_id} not found"))

        page = request.args.get("page", 1, type=int)
        likes = Like.query\
                    .filter_by(post_id=post_id)\
                    .paginate(page, current_app.config["LIKES_PER_PAGE"], False)\
                    .items
        return http_responses.ok(LikeSchema(many=True).dump(likes))


class UserLike(Resource):
    @jwt_required()
    def put(self, post_id):
        """
        Like a post
        ---
        tags:
          - likes
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
            required: true
          - in: path
            name: post_id
            required: true
            type: string
        responses:
          201:
            description: A post's new like
            schema:
              $ref: '#/definitions/LikeResponse'
          401:
            description: Invalid token
          403:
            description: Re-Like not allowed
          404:
            description: Post not found
        """

        post = Post.query.filter_by(id=post_id).first()

        if post is None:
            return http_responses.not_found(error_response(f"Post with id {post_id} not found"))

        like = Like.query.filter_by(post_id=post_id).filter_by(user_id=current_user.id).first()

        if like is not None:
            return http_responses.forbidden(error_response("You cannot like a post twice"))

        like = Like(post=post, user=current_user)
        db.session.add(like)
        db.session.commit()

        return http_responses.created(LikeSchema().dump(like))

    @jwt_required()
    def delete(self, post_id):
        """
        Unlike a post
        ---
        tags:
          - likes
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
            required: true
          - in: path
            name: post_id
            required: true
            type: string
        responses:
          200:
            description: A post's undone like
            schema:
              $ref: '#/definitions/LikeResponse'
          401:
            description: Invalid token
          404:
            description: Post not found
        """

        like = Like.query.filter_by(post_id=post_id).filter_by(user_id=current_user.id).first()

        if like is None:
            return http_responses.not_found(error_response("You haven't like this post yet"))
            
        json_returned = LikeSchema().dump(like)
        db.session.delete(like)
        db.session.commit()

        return http_responses.ok(json_returned)
