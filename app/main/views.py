# -*- coding: utf-8 -*-
from . import mainbp 
from flask import render_template, request

from ..post.models import Post
from ..post.views import _get_categories, _get_archives

@mainbp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.hidden==False).order_by(Post.released_time.desc()).paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('main.html',
            posts=posts,
            pagination=pagination,
            categories=_get_categories(),
            archives=_get_archives(),
            )
