from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    profile_picture = db.Column(db.String(200), nullable=True)  # URL to profile picture

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    candidate = db.relationship('Candidate', backref=db.backref('votes', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'candidate_id', name='_student_candidate_uc'),
    )
