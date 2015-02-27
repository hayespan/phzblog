# -*- coding: utf-8 -*-
from flask import Blueprint

utilbp = Blueprint(
        'util',
        __name__,
        )
from . import views, utils
