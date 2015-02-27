# -*- coding: utf-8 -*-
import os
import re
import json
import datetime
from hashlib import sha1

from flask import render_template, request, redirect, flash, url_for, session, jsonify, abort

from flask.ext.login import login_required, login_user, logout_user, current_user

from .. import db
from . import userbp  
from .forms import LoginForm, ProfileForm
from .models import User, Profile
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
        'access_token': session.get('qq_access_token')[0],
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
    if 'qq_access_token' in session:
        data = update_qq_api_request_data()
        resp = qq_oauth.get('/user/get_user_info', data=data)
        return jsonify(status=resp.status, data=resp.data)
    return redirect(url_for('.oauth_login'))

@userbp.route('/oauthlogin_state/<int:state>')
def oauth_login_state(state):
    if state in (0, -1, -2, -3):
        return render_template('oauthlogin_state.html', state=state)
    abort(404)

@userbp.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def modify_profile(username):
    form = ProfileForm()
    u = current_user
    if request.method == 'GET':
        form.username.data = u.username
        form.email.data = u.email
        return render_template('user_profile.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            u.username = form.username.data
            u.email = form.email.data
            db.session.add(u)
            return redirect(url_for('.modify_profile', username=u.username))
        flash('Invalid username or email.')
        return render_template('user_profile.html', form=form)

@userbp.route('/authorized')
def authorized():
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return redirect(url_for('.oauth_login_state', state=-1)) # csrf attack -- expired
    usercancel = request.args.get('usercancel')
    msg = request.args.get('msg')
    if usercancel or msg:
        return redirect(url_for('.oauth_login_state', state=-2)) # user cancel
    # second step, get access_token
    try:
        data = qq_oauth.handle_oauth2_response()
    except:
        return redirect(url_for('.oauth_login_state', state=-3)) # link failed
    access_token = data['access_token']
    session['qq_access_token'] = (access_token, '') # 0-token, 1-secret
    session.pop('oauth_state')
    res = qq_oauth.get(
            '/oauth2.0/me',
            {'access_token': data['access_token']}
            )
    res = json_to_dict(res.data)
    if isinstance(res, dict):
        openid = res.get('openid')
        session['qq_openid'] = openid
    # get user info
    req_query = update_qq_api_request_data()
    resp = qq_oauth.get('/user/get_user_info', data=req_query)
    user_info = json.loads(resp.data)
    pf = Profile.query.filter_by(openid=openid).first()
    if pf is None:
        u = User(
                username=openid,
                )
        u.password = ''
        if user_info.get('gender') == u'男':
            u.sex = True
        elif user_info.get('gender') == u'女':
            u.sex = False
        else:
            u.sex = None
        pf = u.profile
        pf.nickname = user_info.get('nickname')
        pf.province = user_info.get('province')
        pf.city = user_info.get('city')
        pf.birth = datetime.date(int(user_info.get('year')), 1, 1)
        pf.access_token = access_token
        pf.openid = openid
        db.session.add(pf)
        db.session.commit()
    else:
        u = pf.user
        expired = False
        if pf.access_token != access_token:
            pf.access_token = access_token
            expired = True
        if pf.openid != openid:
            pf.openid = openid
            expired = True
        if expired:
            db.session.add(pf)
    login_user(u, True)
    return redirect(url_for('.oauth_login_state', state=0)) # success

@userbp.route('/oauthlogin')
def oauth_login():
    session['oauth_state'] = sha1(os.urandom(64)).hexdigest()
    return qq_oauth.authorize(callback=url_for('.authorized', _external=True), state=session['oauth_state'])

@qq_oauth.tokengetter
def get_qq_oauth_token():
    return session.get('qq_access_token')

@userbp.route('/a')
@login_required
def _debug():
    form = ProfileForm()
    return render_template('user_profile.html', form=form)

@userbp.route('/testmail')
def _mail():
    from ..util.utils import send_mail
    send_mail('test taskqueue', 'notingbalblaf', ['806968607@qq.com',])
    return 'succceed'

