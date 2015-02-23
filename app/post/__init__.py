# -*- coding: utf-8 -*-
from flask import Blueprint

postbp = Blueprint(
        'post',
        __name__,
        )

from . import views, models
