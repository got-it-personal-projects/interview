import os
from datetime import timedelta
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    LIKES_PER_PAGE = 5
    BODY_OVERVIEW_LENGTH = 100
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "123325145"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    FIREBASE_SDK_KEY = os.getenv("FIREBASE_SDK_KEY")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", None)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMINS = os.getenv("ADMINS").split(",")
    PROPAGATE_EXCEPTIONS = True
    SWAGGER = {
        'uiversion': 3,
        "title": "Blog GotIt APIDocs"
    }


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:quanghuy0211@localhost/blog_gotit"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', '') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
