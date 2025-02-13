from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, company, student
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship('Company', backref='user', lazy=True, uselist=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    company_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    job_listings = db.relationship('JobListing', backref='company', lazy=True)

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    salary_range = db.Column(db.String(50))
    required_skills = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    category = db.Column(db.String(50))  # e.g., "Software", "Marketing"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('JobApplication', backref='job_listing', lazy=True)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_listing_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    date_of_application = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='applied')  # applied/shortlisted/interviewed/selected/rejected
    remarks = db.Column(db.Text)
    resume_link = db.Column(db.String(200))
    expected_salary = db.Column(db.Float)

    student = db.relationship('User', foreign_keys=[student_id], backref='student_applications', lazy=True)
    company = db.relationship('Company', foreign_keys=[company_id], backref='company_applications', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('job_application.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)