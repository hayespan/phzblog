# -*- coding: utf-8 -*-
import re
from datetime import date

from flask import render_template, request, redirect, flash, url_for, session, abort, jsonify
from flask.ext.login import login_required, current_user

from .. import db
from . import postbp  
from .forms import PostForm 
from .models import Post, Tag, Category

# re pattern for matching slugs in tags, categories strings with comma
fetch_slug_rep = u'[,，]?\s*((?:[^,， ]+\s+)*[^,， ]+)\s*[,，]?'

def _is_admin():
    return current_user.is_authenticated and current_user.is_admin

@postbp.route('/<index_name>', methods=['GET'])
def post(index_name):
    post = Post.query.filter_by(index_name=index_name, hidden=False).first()
    if post is None:
        abort(404)
    if not _is_admin():
        post.ping()
    return render_template('post.html', post=post, categories=_get_categories(), archives=_get_archives())

@postbp.route('/create', methods=['GET', 'POST', ])
@login_required
def create_post():
    form = PostForm()
    if request.method == 'GET':
        return render_template('editpost.html', form=form, create=True)
    elif request.method == 'POST':
        if form.validate_on_submit():
            post = Post(
                    title=form.title.data,
                    index_name=form.index_name.data,
                    hidden=form.hidden.data,
                    content=form.post.data,
                    )
            if form.released_time.data is not None:
                post.released_time = form.released_time.data
            db.session.add(post)
            raw_categories = set(re.findall(fetch_slug_rep, form.categories.data))
            for i in raw_categories:
                category = Category.query.filter_by(content=i).first()
                if category is None:
                    category = Category(content=i)
                post.categories.append(category)
            raw_tags = set(re.findall(fetch_slug_rep, form.tags.data))
            for i in raw_tags:
                tag = Tag.query.filter_by(content=i).first()
                if tag is None:
                    tag = Tag(content=i)
                post.tags.append(tag)
            return redirect(url_for('.post', index_name=post.index_name))
        else:
            flash('POST failed.')
            return render_template('editpost.html', form=form, create=True)

@postbp.route('/modify/<index_name>', methods=['GET', 'POST', ])
@login_required
def modify_post(index_name):
    post = Post.query.filter_by(index_name=index_name).first()
    if post is None:
        abort(404)
    form = PostForm()
    if request.method == 'GET':
        form.index_name.data = post.index_name
        form.title.data = post.title
        form.released_time.data = post.released_time
        form.hidden.data = post.hidden
        cgs = ''
        for cg in post.categories.all():
            cgs += cg.content+', '
        form.categories.data = cgs
        tgs = ''
        for tg in post.tags.all():
            tgs += tg.content+', '
        form.tags.data = tgs
        form.post.data = post.content
        return render_template('editpost.html', form=form, create=False, index_name=index_name)
    elif request.method == 'POST':
        if form.validate_on_submit():
            post.title = form.title.data
            post.index_name = form.index_name.data
            post.released_time = form.released_time.data
            post.hidden = form.hidden.data
            post.content = form.post.data
            raw_categories = set(re.findall(fetch_slug_rep, form.categories.data))
            old_categories = set([i.content for i in post.categories.all()])
            for cg in (old_categories-raw_categories):
                c = Category.query.filter_by(content=cg).first()
                post.categories.remove(c)
                if c.posts.count() == 0:
                    db.session.delete(c)
            for cg in (raw_categories-old_categories):
                c = Category.query.filter_by(content=cg).first()
                if not c:
                    c = Category(content=cg)
                    db.session.add(c)
                post.categories.append(c)
            raw_tags = set(re.findall(fetch_slug_rep, form.tags.data))
            old_tags = set([i.content for i in post.tags.all()])
            for tg in (old_tags-raw_tags):
                t = Tag.query.filter_by(content=tg).first()
                post.tags.remove(t)
                if t.posts.count() == 0:
                    db.session.delete(t)
            for tg in (raw_tags-old_tags):
                t = Tag.query.filter_by(content=tg).first()
                if not t:
                    t = Tag(content=tg)
                    db.session.add(t)
                post.tags.append(t)
            db.session.add(post)
            return redirect(url_for('.post', index_name=post.index_name))
@postbp.route('/delete/<index_name>')
@login_required
def post_delete(index_name):
    post = Post.query.filter_by(index_name=index_name).first()
    if post:
        cgs = post.categories.all()
        tgs = post.tags.all()
        db.session.delete(post)
        for i in cgs:
            if i.posts.count() == 0:
                db.session.delete(i)
        for i in tgs:
            if i.posts.count() == 0:
                db.session.delete(i)
    return redirect(url_for('main.index'))

@postbp.route('/list/archive/<int:year>/<int:month>', methods=['GET', ])
def post_list_archive(year, month):
    posts = db.session.query(Post).filter(db.func.year(Post.released_time)==year, db.func.month(Post.released_time)==month, Post.hidden==False).order_by(Post.released_time.desc()).all()
    return render_template('postlist.html', posts=posts, head=u'归档 / %s.%s' %(year, month), categories=_get_categories(), archives=_get_archives())

@postbp.route('/list/category/<category>', methods=['GET', ])
def post_list_category(category):
    cg = Category.query.filter_by(content=category).first()
    posts = []
    if cg:
        posts = cg.posts.filter_by(hidden=False and _is_admin()).order_by(Post.released_time.desc()).all()
    return render_template('postlist.html', head=u'分类 / %s' % cg.content, posts=posts, categories=_get_categories(), archives=_get_archives())

@postbp.route('/list/tag/<tag>', methods=['GET', ])
def post_list_tag(tag):
    tg = Tag.query.filter_by(content=tag).first()
    posts = []
    if tg:
        posts = tg.posts.filter_by(hidden=False and _is_admin()).order_by(Post.released_time.desc()).all()
    return render_template('postlist.html', head=u'标签 / %s' % tg.content, posts=posts, categories=_get_categories(), archives=_get_archives())

@postbp.route('/list', methods=['GET', ])
def post_list():
    posts = Post.query.filter_by(hidden=False and _is_admin()).order_by(Post.released_time.desc()).all()
    return render_template('postlist.html', head=u'全部', posts=posts, categories=_get_categories(), archives=_get_archives())

@postbp.route('/category/list')
def category_list():
    cgs = [[i.id, i.content] for i in Category.query.all()]
    return jsonify({'categories': cgs})

@postbp.route('/tag/list')
def tag_list():
    tgs = [[i.id, i.content] for i in Tag.query.all()]
    return jsonify({'tags': tgs})

def _get_categories():
    return Category.query.all()
def _get_archives():
    return list(map(lambda x: [date(x[0],x[1],1).strftime('%Y.%m'), x[2]], db.session.query(db.func.year(Post.released_time), db.func.month(Post.released_time), db.func.count('*')).group_by(db.func.year(Post.released_time), db.func.month(Post.released_time)).all()))
