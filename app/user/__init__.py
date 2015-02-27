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
@userbp.record_once
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
            access_token_url='/oauth2.0/token',
            authorize_url='/oauth2.0/authorize'
            )
    def convert_keys_to_string(dictionary):
        """Recursively converts dictionary keys to strings."""
        if not isinstance(dictionary, dict):
            return dictionary
        return dict((str(k), convert_keys_to_string(v))
            for k, v in dictionary.items())

    def change_qq_header(uri, headers, body):
        headers = convert_keys_to_string(headers)
        return uri, headers, body

    qq_oauth.pre_request = change_qq_header

    # inject globals.avatar_base_url using app context_processor
    @app.context_processor
    def avatar_url():
        return dict(avatar_base_url='http://q.qlogo.cn/qqapp/' + app.config.get('QQ_APP_ID') + '/%s/100')

    from . import views, models

