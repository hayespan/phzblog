# -*- coding: utf-8 -*-
from functools import wraps
from flask import abort
from flask.ext.login import current_user

def admin_required(func):
    '''admin required decorator'''
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(404)
        return func(*args, **kwargs)
    return wrapped

def _is_admin():
    return current_user.is_authenticated and current_user.is_admin

