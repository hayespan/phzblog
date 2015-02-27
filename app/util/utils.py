# -*- coding: utf-8 -*-
from flask import url_for
from sae.taskqueue import Task, TaskQueue
import json

queue = TaskQueue('mailq')

def send_mail(subject='', body='', recipients=None, reply_to='hayespan@qq.com'):
    queue.add(Task(url_for('util.send_mail'),
        json.dumps({
            'subject': subject,
            'body': body,
            'recipients': recipients,
            'reply_to': reply_to,
            })
        ))
