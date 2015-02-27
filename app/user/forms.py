# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Optional, Email, Length, Regexp

from flask.ext.wtf import Form

class LoginForm(Form):
    username = StringField(validators=[Required(), Length(1, 64), ])
    password = PasswordField(validators=[Required(), ])
    remember_me = BooleanField()

class ProfileForm(Form):
    username = StringField(validators=[Required(), Length(1, 32), Regexp(r'^[\w]+$')])
    email = StringField(validators=[Optional(), Email(), ])
    submit = SubmitField()
    
