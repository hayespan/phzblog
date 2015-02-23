# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length

from flask.ext.wtf import Form

class LoginForm(Form):
    username = StringField(validators=[Required(), Length(1, 64), ])
    password = PasswordField(validators=[Required(), ])
    remember_me = BooleanField()
