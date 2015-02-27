# -*- coding: utf-8 -*-
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from .. import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(75), nullable=True, unique=True)

    sex = db.Column(db.Boolean, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.profile is None:
            self.profile = Profile()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.is_active
        
    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)

class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nickname = db.Column(db.String(30), nullable=False, default='')
    province = db.Column(db.String(10), nullable=True) 
    city = db.Column(db.String(20), nullable=True)
    birth = db.Column(db.Date(), nullable=True)
    access_token = db.Column(db.String(32))
    openid = db.Column(db.String(32))
    def __repr__(self):
        return '<Profile %d %s>' % (self.id, self.user.username)

from .. import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask.ext.login import AnonymousUserMixin
class MyAnonymousUser(AnonymousUserMixin):
    is_admin = False
login_manager.anonymous_user = MyAnonymousUser

