from flask import request
from flask import current_app
from flask_restful import Resource
from flask_restful import reqparse
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from app import db
from app.models import Post
from app.schemas import PostSchema
from app.schemas import PostListSchema
from app.utils.errors import error_response
from app.utils import http_responses


class PostList(Resource):
    @jwt_required()
    def get(self):
        """
        Get list of posts
        ---
        tags:
          - posts
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
            required: true
        responses:
          200:
            description: List of posts
            schema:
              type: array
              items:
                $ref: '#/definitions/PostResponse'
          401:
            description: Invalid token
        """

        page = request.args.get("page", 1, type=int)
        posts = Post.query\
                    .order_by(Post.created_at.desc())\
                    .paginate(page, current_app.config["POSTS_PER_PAGE"], False)\
                    .items
        return http_responses.ok(PostListSchema(many=True).dump(posts))


class PostUpload(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title", type=str, required=True, help="Title is required")
    parser.add_argument("body", type=str, required=True, help="Body is required")
    
    @jwt_required()
    def post(self):
        """
        Create a post
        ---
        tags:
          - posts
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
            required: true
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/CreateBody'
        definitions:
          CreateBody:
            type: object
            properties:
              title:
                type: string
              body:
                type: string
        responses:
          201:
            description: Created post
            schema:
              $ref: '#/definitions/PostResponse'
          401:
            description: Invalid token
        """

        args = self.parser.parse_args()
        post = Post(author=current_user, **args)
        db.session.add(post)
        db.session.commit()
        return http_responses.created(PostSchema().dump(post))


class PostDetail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title", type=str, required=True, help="Title is required")
    parser.add_argument("body", type=str, required=True, help="Body is required")
    
    @jwt_required()
    def get(self, post_id):
        """
        Get post detail
        ---
        tags:
          - posts
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
            description: Post detail
            schema:
              $ref: '#/definitions/PostResponse'
          401:
            description: Invalid token
          404:
            description: Post not found
        """

        post = Post.query.filter_by(id=post_id).first()

        if post is None:
            return http_responses.not_found(error_response(f"Post with id {post_id} not found"))

        return http_responses.ok(PostSchema().dump(post))

    @jwt_required()
    def put(self, post_id):
        """
        Update post detail
        ---
        tags:
          - posts
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
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/UpdateBody'
        definitions:
          UpdateBody:
            type: object
            properties:
              title:
                type: string
              body:
                type: string
        responses:
          200:
            description: Updated Post detail
            schema:
              $ref: '#/definitions/PostResponse'
          401:
            description: Invalid token
          403:
            description: Update not allowed
          404:
            description: Post not found
        """

        args = self.parser.parse_args()
        post = Post.query.filter_by(id=post_id).first()
        
        if post is None:
            return http_responses.not_found(error_response(f"Post with id {post_id} not found"))

        if post.author != current_user:
            return http_responses.forbidden(error_response("You are the author of this post"))

        post.title = args["title"]
        post.body = args["body"]
        db.session.add(post)
        db.session.commit()
        return http_responses.ok(PostSchema().dump(post))

    @jwt_required()
    def delete(self, post_id):
        """
        Delete the post
        ---
        tags:
          - posts
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
            description: Deleted post
            schema:
              $ref: '#/definitions/PostResponse'
          401:
            description: Invalid token
          403:
            description: Delete not allowed
          404:
            description: Post not found
        """

        post = Post.query.filter_by(id=post_id).first()
        
        if post is None:
            return http_responses.not_found(error_response(f"Post with id {post_id} not found"))

        if post.author != current_user:
            return http_responses.forbidden(error_response("You are the author of this post"))

        json_returned = PostSchema().dump(post)
        db.session.delete(post)
        db.session.commit()

        return http_responses.ok(json_returned)
