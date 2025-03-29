from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    _password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True,  nullable=False, index=True)
    description = db.Column(db.Text)
 
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    subject = db.relationship('Subject', backref=db.backref('chapters', lazy="dynamic", cascade="all, delete"))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    date_of_quiz = db.Column(db.Date)
    time_duration = db.Column(db.String(10))
    remarks = db.Column(db.Text)

    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy="dynamic", cascade="all, delete"))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False, index=True)
    question_statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(100))
    option_2 = db.Column(db.String(100))
    option_3 = db.Column(db.String(100))
    option_4 = db.Column(db.String(100))
    correct_option = db.Column(db.Integer)

    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy="dynamic", cascade="all, delete"))

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True)
    time_stamp_of_attempt = db.Column(db.DateTime)
    total_scored = db.Column(db.Integer)
    completion_minutes = db.Column(db.Integer)
    completion_seconds = db.Column(db.Integer)

    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy="dynamic", cascade="all, delete"))
    user = db.relationship('User', backref=db.backref('scores', lazy="dynamic", cascade="all, delete"))