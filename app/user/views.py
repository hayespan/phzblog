# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, flash, url_for, session

from flask.ext.login import login_required, login_user, logout_user

from . import userbp  
from .forms import LoginForm
from .models import User

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
