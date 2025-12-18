from datetime import datetime, timezone
from typing import List, Optional

from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    user = db.session.get(Author, int(id))
    if user:
        return user
    return db.session.get(Viewer, int(id))

posts_tags = sqla.Table(
    'posts_tags',
    db.metadata,
    sqla.Column('post_id', sqla.Integer, sqla.ForeignKey('post.id'), primary_key=True),
    sqla.Column('tag_name', sqla.String, sqla.ForeignKey('tag.name'), primary_key=True)
)

class User(db.Model, UserMixin):
    __abstract__ = True
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    username: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)
    email: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120), unique=True, index=True)
    password_hash: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Viewer(User):
    __tablename__ = 'viewer'    
    comments: sqlo.Mapped[List['Comment']] = sqlo.relationship(back_populates='viewer')

    def __repr__(self):
        return f'<Viewer {self.username}>'


class Author(User):
    __tablename__ = 'author'
    posts: sqlo.Mapped[List['Post']] = sqlo.relationship(back_populates='author')
    comments: sqlo.Mapped[List['Comment']] = sqlo.relationship(back_populates='author')

    def __repr__(self):
        return f'<Author {self.username}>'


class Post(db.Model):
    __tablename__ = 'post'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    description: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(512))
    date: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))
    author_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('author.id'))
    
    author: sqlo.Mapped['Author'] = sqlo.relationship(back_populates='posts')
    comments: sqlo.Mapped[List['Comment']] = sqlo.relationship(back_populates='post')
    tags: sqlo.Mapped[List['Tag']] = sqlo.relationship(secondary=posts_tags, back_populates='posts')

    def __repr__(self):
        return f'<Post {self.name}>'

class Comment(db.Model):
    __tablename__ = 'application'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    viewer_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('viewer.id'))
    post_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('post.id'))
    statement: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(1500))
    status: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), default="pending")
    created_at: sqlo.Mapped[datetime] = sqlo.mapped_column(
        sqla.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    author_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('author.id'))

    viewer: sqlo.Mapped['Viewer'] = sqlo.relationship(back_populates='comments')
    post: sqlo.Mapped['Post'] = sqlo.relationship(back_populates='comments')
    author: sqlo.Mapped['Author'] = sqlo.relationship(back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'

class Tag(db.Model):
    __tablename__ = 'tag'
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100), primary_key=True)

    posts: sqlo.Mapped[List['Post']] = sqlo.relationship(secondary=posts_tags, back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name}>'