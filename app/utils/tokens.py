from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token


def create_tokens(user):
    return {
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(user.id)
    }
