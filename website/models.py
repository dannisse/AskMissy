from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


students = db.Table('students',
        db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('Class_group', db.Integer, db.ForeignKey('classgroup.id'), primary_key=True)
)


class Classgroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_num = db.Column(db.Integer)
    class_name = db.Column(db.String(150))
    teacher = db.Column(db.String(150))
    announcements = db.relationship('Note')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    students = db.relationship('User', secondary=students, lazy='subquery',
                               backref=db.backref('users', lazy=True))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classgroup.id'))
    class_color = db.Column(db.String(10000))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    user_type = db.Column(db.String(150))
    school = db.Column(db.String(150))
    notes = db.relationship('Note')
    message = db.relationship('Message')
    classgroup = db.relationship('Classgroup')


class Bookreq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    authors = db.Column(db.String(150))
    publication_data = db.Column(db.String(4))
    isbn = db.Column(db.Integer)


class Books(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    goodreads_book_id = db.Column(db.Integer)
    isbn = db.Column(db.Integer)
    authors = db.Column(db.String(150))
    original_publication_year = db.Column(db.String(4))
    title = db.Column(db.String(150))
    average_rating = db.Column(db.Numeric(10,2))
    image_url = db.Column(db.String(200))
    small_image_url = db.Column(db.String(200))
    ratings = db.relationship('Ratings')
    book_tags = db.relationship('Booktags')

class Tags(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(150))
    book_tags = db.relationship('Booktags')

class Booktags(db.Model):
    book_tag_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'))
    count = db.Column(db.Integer)


class Ratings(db.Model):
    ratings_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    rating = db.Column(db.Integer)
