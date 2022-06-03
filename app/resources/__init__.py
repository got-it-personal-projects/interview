from flask import Blueprint


bp = Blueprint('api', __name__)


from flask_restful import Api
from app.resources.users import FbRegister
from app.resources.users import FbProfile
from app.resources.users import GgRegister
from app.resources.users import GgProfile
from app.resources.auth import TokenRefresh
from app.resources.auth import FbLogin
from app.resources.auth import GgLogin
from app.resources.posts import PostList
from app.resources.posts import PostDetail
from app.resources.posts import PostUpload
from app.resources.likes import UserLike
from app.resources.likes import PostLikeList


api = Api(bp)

api.add_resource(FbRegister, "/users/registrations/facebook")
api.add_resource(FbProfile, "/users/me/facebook")
api.add_resource(GgRegister, "/users/registrations/google")
api.add_resource(GgProfile, "/users/me/google")
api.add_resource(TokenRefresh, "/auth/token_refresh")
api.add_resource(FbLogin, "/auth/facebook")
api.add_resource(GgLogin, "/auth/google")
api.add_resource(PostList, "/posts")
api.add_resource(PostUpload, "/posts")
api.add_resource(PostDetail, "/posts/<int:post_id>")
api.add_resource(PostLikeList, "/posts/<int:post_id>/likes")
api.add_resource(UserLike, "/users/me/likes/<int:post_id>")
