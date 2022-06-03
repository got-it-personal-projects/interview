from flask_restful import Resource
from flask_restful import reqparse
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from app import db
from app import services
from app.models import Like
from app.models import User
from app.models import FacebookAuth
from app.models import Post
from app.models import GoogleAuth
from app.utils.tokens import create_tokens
from app.utils.errors import error_response
from app.utils import http_responses
from app.schemas import PostListSchema


class FbRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("accessToken", type=str, required=True, help="Access Token is required")
    parser.add_argument("userId", type=str, required=True, help="User Id is required")

    def post(self):
        """
        Register a Facebook user
        ---
        tags:
          - users
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/RegisterBody'
        definitions:
          RegisterBody:
            type: object
            properties:
              accessToken:
                type: string
              userId:
                type: string
        responses:
          201:
            description: A newly created Facebook user
            schema:
              $ref: '#/definitions/GeneratedTokensResponse'
          400:
            description: Account existed
          401:
            description: Invalid Access Token
        """

        args = self.parser.parse_args()
        resp = services.facebook_auth.get_user(args["accessToken"])
        
        if "error" in resp:
            return http_responses.unauthorized(resp)

        if resp["id"] != args["userId"]:
            return http_responses.bad_request(error_response("Invalid Access Token"))

        if GoogleAuth.query.filter_by(email=resp["email"]).first():
            return http_responses.bad_request(error_response(f"Account with {resp['email']} has been registered from Google"))

        if FacebookAuth.query.filter_by(email=resp["email"]).first():
            return http_responses.bad_request(error_response(f"Account with {resp['email']} is existed"))
        
        user = User(name=resp["name"])
        fb_auth = FacebookAuth(email=resp["email"], fb_user_id=resp["id"], user=user)
        db.session.add(user)
        db.session.add(fb_auth)
        db.session.commit()
        return http_responses.created(create_tokens(user))


class FbProfile(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="Name is required")
    parser.add_argument("phone", type=str, required=True, help="Phone Number is required")

    def __to_dict(self):
        phone = FacebookAuth.query.filter_by(user_id=current_user.id).first().phone

        return {
            "id": current_user.id,
            "name": current_user.name,
            "phone": phone and phone.national,
            "posts": PostListSchema(many=True).dump(Post.query.filter_by(author_id=current_user.id).all())
        }

    @jwt_required()
    def get(self):
        """
        Get current Facebook user's profile
        ---
        tags:
          - users
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            required: true
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
        responses:
          200:
            description: Current Facebook user's profile
            schema:
              $ref: '#/definitions/FbUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        if FacebookAuth.query.filter_by(user_id=current_user.id).first() is None:
            return http_responses.not_found(error_response(f"You haven't register a Facebook account"))

        return http_responses.ok(self.__to_dict())

    @jwt_required()
    def put(self):
        """
        Update current Facebook user's profile
        ---
        tags:
          - users
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the access token
            required: true
            schema:
              type: bearer
              example: Bearer <JWT Access Token>
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/UpdateBody'
        definitions:
          UpdateBody:
            type: object
            properties:
              name:
                type: string
              phone:
                type: string
        responses:
          200:
            description: Current Facebook user's profile
            schema:
              $ref: '#/definitions/FbUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        args = self.parser.parse_args()
        
        fb_auth = FacebookAuth.query.filter_by(user_id=current_user.id).first()
        if fb_auth is None:
            return http_responses.not_found(error_response("You haven't register a Facebook account"))

        current_user.name = args["name"]
        fb_auth.phone = args["phone"]
        db.session.add(current_user)
        db.session.add(fb_auth)
        db.session.commit()
        return http_responses.ok(self.__to_dict())

    @jwt_required()
    def delete(self):
        """
        Delete current Facebook user's profile
        ---
        tags:
          - users
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
            description: Current Facebook user's profile
            schema:
              $ref: '#/definitions/FbUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        fb_auth = FacebookAuth.query.filter_by(user_id=current_user.id).first()

        if fb_auth is None:
            return http_responses.not_found(error_response("You haven't register a Facebook account"))

        json_returned = self.__to_dict()
        db.session.delete(fb_auth)
        Like.query.filter_by(user_id=current_user.id).delete()
        Post.query.filter_by(author_id=current_user.id).delete()
        db.session.delete(current_user)
        db.session.commit()
        return http_responses.ok(json_returned)


class GgRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("accessToken", type=str, required=True, help="Access Token is required")
    parser.add_argument("userId", type=str, required=True, help="User ID is required")

    def post(self):
        """
        Register a Google user
        ---
        tags:
          - users
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/RegisterBody'
        definitions:
          RegisterBody:
            type: object
            properties:
              accessToken:
                type: string
              userId:
                type: string
        responses:
          201:
            description: A newly created Google user
            schema:
              $ref: '#/definitions/GeneratedTokensResponse'
          400:
            description: Account existed
          401:
            description: Invalid Access Token
        """

        args = self.parser.parse_args()
        resp = services.google_auth.get_user(args["accessToken"])

        if resp is None or resp["user_id"] != args["userId"]:
            return http_responses.bad_request(error_response("Invalid Access Token"))

        if FacebookAuth.query.filter_by(email=resp["email"]).first():
            services.google_auth.delete_user(resp["user_id"])
            return http_responses.bad_request(error_response(f"Account with {resp['email']} has been registered from Facebook"))

        if GoogleAuth.query.filter_by(email=resp["email"]).first():
            return http_responses.bad_request(error_response(f"Account with {resp['email']} is existed"))

        user = User(name=resp["name"])
        gg_auth = GoogleAuth(email=resp["email"], gg_user_id=resp["user_id"], user=user)
        db.session.add(user)
        db.session.add(gg_auth)
        db.session.commit()
        return http_responses.created(create_tokens(user))


class GgProfile(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="Name is required")
    parser.add_argument("occupation", type=str, required=True, help="Occupation is required")

    def __to_dict(self):
        return {
            "id": current_user.id,
            "name": current_user.name,
            "occupation": GoogleAuth.query.filter_by(user_id=current_user.id).first().occupation,
            "posts": PostListSchema(many=True).dump(Post.query.filter_by(author_id=current_user.id).all())
        }

    @jwt_required()
    def get(self):
        """
        Get current Google user's profile
        ---
        tags:
          - users
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
            description: Current Google user's profile
            schema:
              $ref: '#/definitions/GgUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        if GoogleAuth.query.filter_by(user_id=current_user.id).first() is None:
            return http_responses.not_found(error_response(f"You haven't register a Google account"))

        return http_responses.ok(self.__to_dict())

    @jwt_required()
    def put(self):
        """
        Update current Google user's profile
        ---
        tags:
          - users
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
              $ref: '#/definitions/UpdateBody'
        definitions:
          UpdateBody:
            type: object
            properties:
              name:
                type: string
              occupation:
                type: string
        responses:
          200:
            description: Current Google user's profile
            schema:
              $ref: '#/definitions/GgUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        args = self.parser.parse_args()
        
        gg_auth = GoogleAuth.query.filter_by(user_id=current_user.id).first()
        if gg_auth is None:
            return http_responses.not_found(error_response(f"You haven't register a Google account"))

        current_user.name = args["name"]
        gg_auth.occupation = args["occupation"]
        db.session.add(current_user)
        db.session.add(gg_auth)
        db.session.commit()
        return http_responses.ok(self.__to_dict())

    @jwt_required()
    def delete(self):
        """
        Delete current Google user's profile
        ---
        tags:
          - users
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
            description: Current Google user's profile
            schema:
              $ref: '#/definitions/GgUserProfileResponse'
          401:
            description: Invalid token
          404:
            description: Current user not found
        """

        gg_auth = GoogleAuth.query.filter_by(user_id=current_user.id).first()

        if gg_auth is None:
            return http_responses.not_found(error_response("You haven't register a Google account"))

        json_returned = self.__to_dict()
        db.session.delete(gg_auth)
        Like.query.filter_by(user_id=current_user.id).delete()
        Post.query.filter_by(author_id=current_user.id).delete()
        db.session.delete(current_user)
        db.session.commit()
        return http_responses.ok(json_returned)
