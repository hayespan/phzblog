# -*- coding: utf-8 -*-
from flask import Flask


# flask-SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()
# flask-oauth
from flask.ext.oauthlib.client import OAuth
oauth = OAuth()
# flask-login
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'user.login'

# app factory class
class App(object):
    def __init__(self, **kwargs):
        self.app = Flask(__name__, instance_relative_config=True)
        # config -- public config 
        self.app.config.from_object('config')
        # instance/config.py -- private config
        self.app.config.from_pyfile('config.py')
        # config/xxx.py -- scence config
        # self.app.config.from_envvar('APP_CONFIG_FILE') # APP_CONFIG_FILE defined in start.sh

        # flask-SQLAlchemy
        db.init_app(self.app)

        # flask-login
        login_manager.init_app(self.app)

        # flask-migrate
        from flask.ext.migrate import Migrate, MigrateCommand
        self.migrate = Migrate(self.app, db)

        # flask-script
        from flask.ext.script import Manager, Shell 
        self.manager = Manager(self.app)
        # add 'db' command for flask-migrate
        self.manager.add_command('db', MigrateCommand)

        oauth.init_app(self.app)

        # pre-import some class for convenience
        def make_shell_context():
            from .user.models import User, Profile
            from .post.models import Post, Tag, Category
            return dict(app=self.app,
                    db=db,
                    User=User,
                    Profile=Profile,
                    Post=Post,
                    Tag=Tag,
                    Category=Category,
                    )
        self.manager.add_command('shell', Shell(make_context=make_shell_context))

        # flask-moment
        from flask.ext.moment import Moment
        self.moment = Moment(self.app)

        for k,v in kwargs.items():
            setattr(self.app, k, v)

        # main blog app
        from .main import mainbp
        self.app.register_blueprint(
                mainbp,
                # url_prefix='',
                )
        # user & auth app
        from .user import userbp
        self.app.register_blueprint(
                userbp,
                url_prefix='/user',
                )
        # post 
        from .post import postbp
        self.app.register_blueprint(
                postbp,
                url_prefix='/post'
                )

