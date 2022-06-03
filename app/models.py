from datetime import datetime
from sqlalchemy_utils import EmailType
from sqlalchemy_utils import PhoneNumberType
from app import db
from app.utils.string_manipulation import random_string


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(25), nullable=False, default=random_string())

    def __repr__(self):
        return f"<User (name={self.name})>"


class FacebookAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fb_user_id = db.Column(db.String(128), nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False, index=True)
    phone = db.Column(PhoneNumberType)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", uselist=False)

    def __repr__(self):
        return f"<FacebookAuth (email={self.email}, user={self.user})>"


class GoogleAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gg_user_id = db.Column(db.String(128), nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False, index=True)
    occupation = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", uselist=False)

    def __repr__(self):
        return f"<GoogleAuth (email={self.email}, user={self.user})>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    author = db.relationship("User", uselist=False)
    likes = db.relationship("Like", backref="post", cascade="all,delete", lazy="dynamic")

    def __repr__(self):
        return f"<Post (title={self.title}, author={self.author})>"


class Like(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

    user = db.relationship("User", uselist=False)

    def __repr__(self):
        return f"<Like (post={self.post}, user={self.user})>"
