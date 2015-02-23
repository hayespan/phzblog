# -*- coding: utf-8 -*-
from .. import db
from datetime import datetime

post_tag_association = db.Table(
    'post_tag_association',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), nullable=False),
    db.UniqueConstraint('post_id', 'tag_id'),
    )

post_category_association = db.Table(
    'post_category_association',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), nullable=False),
    db.UniqueConstraint('post_id', 'category_id'),
    )
    
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    index_name = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(50), default='', nullable=False)
    released_time = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    modified_time = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    content = db.Column(db.Text(), nullable=False, default='')
    categories = db.relationship('Category', secondary=post_category_association, backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tag_association, backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')
    read_cnt = db.Column(db.Integer, default=0, nullable=False)
    
    def ping(self):
        self.read_cnt += 1
        db.session.add(self)

    def __repr__(self):
        return '<Post %d %s>' % (self.id, self.title.encode('utf-8'))

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30), default='', nullable=False)

    def __repr__(self):
        return '<Category %d %s>' % (self.id, self.content.encode('utf-8'))

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30), default='', nullable=False)

    def __repr__(self):
        return '<Tag %d %s>' % (self.id, self.content.encode('utf-8'))

