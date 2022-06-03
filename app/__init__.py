import os
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler
import firebase_admin
from firebase_admin import credentials
from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flasgger import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from app.docs.schemas import GeneratedTokensResponseSchema, GgUserProfileResponseSchema
from app.docs.schemas import FbUserProfileResponseSchema
from app.docs.schemas import LikeResponseSchema
from app.utils.errors import error_response
from app.utils import http_responses
from app.utils.logging.formatters import RequestFormatter
from config import Config


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
jwt = JWTManager()

ver = "v1"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    _init_extensions(app)
    _init_error_handler(app)
    _init_blueprint(app)
    _init_logging(app)
    _init_db(app)
    _init_docs(app)

    return app


def _init_db(app):
    @app.before_first_request
    def init_db():
        db.create_all()


def _init_blueprint(app):
    from app.resources import bp as api_bp
    app.register_blueprint(api_bp, url_prefix=f"/api/{ver}")


def _init_error_handler(app):
    @app.errorhandler(404)
    def handle_url_not_found(e):
        return http_responses.not_found(jsonify(error_response("The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.")))

    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(e)
        return http_responses.internal_server_error(jsonify(error_response("An unexpected error has occurred")))

    @app.errorhandler(Exception)
    def handle_internal_error(e):
        print(e)
        app.logger.error(e)
        return http_responses.internal_server_error(jsonify(error_response("An unexpected error has occurred")))


def _init_extensions(app):
    cred = credentials.Certificate(app.config["FIREBASE_SDK_KEY"])
    firebase_admin.initialize_app(cred)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)


def _init_docs(app):
    spec = APISpec(
        title="Blog GotIt APIDocs",
        version="1.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
            MarshmallowPlugin()
        ]
    )
    template = spec.to_flasgger(app, definitions=[
        GeneratedTokensResponseSchema,
        FbUserProfileResponseSchema,
        GgUserProfileResponseSchema,
        LikeResponseSchema
    ])
    template["info"]["description"] = \
        "API Documentation for Blog GotIt Backend" + \
        "<style>.models {display: none !important}</style>" + \
        "<style>.topbar {display: none !important}</style>"
    Swagger(app, template=template)


def _init_logging(app):
    if not app.debug and not app.testing:
        formatter = RequestFormatter(
            '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
            '%(levelname)s in %(module)s: %(message)s'
        )

        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs=app.config["ADMINS"],
                subject="Blog Failure",
                credentials=auth,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        file_handler = RotatingFileHandler("logs/server.log", maxBytes=10240, backupCount=10)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Server Startup")


from app import models
