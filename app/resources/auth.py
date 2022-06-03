from flask import jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import UserLookupError
from flask_restful import Resource
from flask_restful import reqparse
from app import jwt
from app import services
from app.models import FacebookAuth
from app.models import GoogleAuth
from app.models import User
from app.utils.tokens import create_tokens
from app.utils.errors import error_response
from app.utils import http_responses
from app.resources import bp


@bp.app_errorhandler(UserLookupError)
def handle_user_lookup_error(e):
    return http_responses.unauthorized(jsonify(error_response("User not found")))


@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).first()


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh expired access token
        ---
        tags:
          - auth
        parameters:
          - in: header
            name: Authorization
            description: You have to log in/register first to get the refresh token
            schema:
              type: bearer
              example: Bearer <JWT Refresh Token>
            required: true
        definitions:
          NewAccessToken:
            type: object
            properties:
              access_token: 
                type: string
        responses:
          201:
            description: New access token
            schema:
              $ref: '#/definitions/NewAccessToken'
        """

        current_user = get_jwt_identity()
        return http_responses.created({"access_token": create_access_token(identity=current_user)})


class FbLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("accessToken", type=str, required=True, help="Access Token is required")

    def post(self):
        """
        Log a Facebook user in
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/LoginBody'
        definitions:
          LoginBody:
            type: object
            properties:
              accessToken:
                type: string
        responses:
          200:
            description: User logged in
            schema:
              $ref: '#/definitions/GeneratedTokensResponse'
          401:
            description: Invalid Access Token
          404:
            description: User not found
        """

        args = self.parser.parse_args()
        resp = services.facebook_auth.get_user(args["accessToken"])

        if "error" in resp:
            return http_responses.unauthorized(resp)

        fb_auth = FacebookAuth.query.filter_by(email=resp["email"]).first()

        if fb_auth is None:
            return http_responses.not_found(error_response(f"User with email {resp['email']} not found"))

        return http_responses.ok(create_tokens(fb_auth.user))


class GgLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("accessToken", type=str, required=True, help="Access Token is required")

    def post(self):
        """
        Log a Google user in
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/LoginBody'
        definitions:
          LoginBody:
            type: object
            properties:
              accessToken:
                type: string
        responses:
          200:
            description: User logged in
            schema:
              $ref: '#/definitions/GeneratedTokensResponse'
          401:
            description: Invalid Access Token
          404:
            description: User not found
        """

        args = self.parser.parse_args()
        resp = services.google_auth.get_user(args["accessToken"])

        if resp is None:
            return http_responses.unauthorized(error_response("Invalid Access Token"))

        gg_auth = GoogleAuth.query.filter_by(email=resp["email"]).first()

        if gg_auth is None:
            return http_responses.not_found(error_response(f"User with email {resp['email']} not found"))

        return http_responses.ok(create_tokens(gg_auth.user))
