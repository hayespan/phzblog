# -*- coding: utf-8 -*-
import re

from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, SubmitField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class PostForm(Form):
    title = StringField(validators=[Required(), Length(1, 50), ])
    index_name = StringField(validators=[Required(),Length(1, 50), Regexp(r'^[\w\-\_]+$'), ])
    released_time = DateField(validators=[Optional(), ])
    hidden = BooleanField()
    categories = StringField(validators=[Required(), ])
    tags = StringField(validators=[Required(), ])
    post = TextAreaField()
    submit = SubmitField()

    # def validate_index_name(self, field):
        # if re.match(r'^[\w\-\_]+$', field.data) is None: 
            # raise ValidationError()

