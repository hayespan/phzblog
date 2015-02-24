# -*- coding: utf-8 -*-
from flask import Blueprint

userbp = Blueprint(
        'user',
        __name__,
        # if templates & static dirs are in
        # subapp/ then the following configs
        # are needed.
        # template_folder='templates',
        # static_folder='static'.
        )

qq_oauth = None
@userbp.record
def import_qq_oauth_config(setup_state):
    global qq_oauth
    from .. import oauth
    app = setup_state.app
    qq_oauth = oauth.remote_app(
            'qq',
            consumer_key=app.config.get('QQ_APP_ID'),
            consumer_secret=app.config.get('QQ_APP_KEY'),
            base_url='https://graph.qq.com',
            request_token_url=None,
            request_token_params={'scope': 'get_user_info'},
            access_token_params={
                'client_id': app.config.get('QQ_APP_ID'),
                'grant_type': 'authorization_code'
                },
            access_token_url='/oauth2.0/token',
            authorize_url='/oauth2.0/authorize'
            )
    from . import views, models

