# -*- coding: utf-8 -*-
import json
from flask import render_template, request, redirect, flash, url_for, session

from flask.ext.login import login_required, login_user, logout_user

from . import userbp  
from .forms import LoginForm
from .models import User
from . import qq_oauth

@userbp.route('/register')
def register():
    pass

@userbp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@userbp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@userbp.route('/login_required', methods=['GET'])
@login_required
def test_login_required():
    return 'secret'

def update_qq_api_request_data(data={}):
    '''Update some required parameters for OAuth2.0 API calls'''
    defaults = {
        'openid': session.get('qq_openid'),
        'access_token': session.get('qq_token')[0],
        'oauth_consumer_key': qq_oauth.consumer_key,
        }
    defaults.update(data)
    return defaults

def json_to_dict(x):
    '''OAuthResponse class can't not parse the JSON data with content-type
text/html, so we need reload the JSON data manually'''
    if x.find('callback') > -1:
        pos_lb = x.find('{')
        pos_rb = x.find('}')
        x = x[pos_lb:pos_rb + 1]
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x

@userbp.route('/user_info')
def get_user_info():
    if 'qq_token' in session:
        data = update_qq_api_request_data()
        resp = qq_oauth.get('/user/get_user_info', data=data)
        return jsonify(status=resp.status, data=resp.data)
    return redirect(url_for('oauth_login'))

@userbp.route('/authorized')
def authorized():
    res = qq_oauth.authorized_response()
    if res is None:
        return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
                )
    session['qq_token'] = (res['access_token'], '')
    # Get openid via access_token, openid and access_token are needed for API calls
    res = qq_oauth.get(
            '/oauth2.0/me',
            {'access_token': session['qq_token'][0]}
            )
    res = json_to_dict(res.data)
    if isinstance(res, dict):
        session['qq_openid'] = res.get('openid')
    return redirect(url_for('get_user_info'))

@userbp.route('/oauthlogin')
def oauth_login():
    return qq_oauth.authorize(callback=url_for('.authorized', _external=True))

