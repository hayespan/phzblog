# -*- coding: utf-8 -*-
from . import utilbp
from .. import db
# @utilbp.route('/initdb')
def initdb():
    db.create_all()
    return 'succeed.'
    
