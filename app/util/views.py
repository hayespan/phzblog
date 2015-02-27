# -*- coding: utf-8 -*-
from . import utilbp
from .. import db
from flask import request

@utilbp.route('/initdb')
def initdb():
    db.create_all()
    return 'succeed.'

import json
from flask.ext.mail import Message
from .. import mail
@utilbp.route('/sendmail', methods=['POST',])
def send_mail():
    try:
        data = json.loads(request.get_data())
    except:
        pass
    msg = Message(
            subject=data['subject'],
            recipients=data['recipients'],
            body=data['body'],
            reply_to=data['reply_to'],
            )
    mail.send(msg)
