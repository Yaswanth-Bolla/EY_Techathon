from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Company, JobListing, JobApplication, Review
from app.forms import (RegistrationForm, LoginForm, CompanyProfileForm, 
                       JobListingForm, JobApplicationForm, ReviewForm)
from flask import Blueprint
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route("/")
def home():
    jobs = JobListing.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', jobs=jobs)

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()

        if form.role.data == 'company':
            company = Company(
                user_id=user.id,
                company_name=form.company_name.data,
                description=form.description.data,
                is_approved=False
            )
            db.session.add(company)
            db.session.commit()
            flash('Your company account has been created! Please wait for admin approval before posting jobs.', 'info')
        else:
            flash('Your student account has been created! You can now log in.', 'success')
        
        return redirect(url_for('main.login'))
    
    return render_template('register.html', title='Register', form=form)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('No account found with this email.', 'danger')
            return render_template('login.html', title='Login', form=form)
            
        if not bcrypt.check_password_hash(user.password, form.password.data):
            flash('Incorrect password.', 'danger')
            return render_template('login.html', title='Login', form=form)
            
        login_user(user)
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif user.role == 'company':
            return redirect(url_for('main.company_dashboard'))
        else:
            return redirect(url_for('main.student_dashboard'))
    
    return render_template('login.html', title='Login', form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route("/student_dashboard")
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    # Get all job applications by the student
    applications = JobApplication.query.filter_by(student_id=current_user.id).order_by(JobApplication.date_of_application.desc()).all()
    
    # Get recommended jobs based on student's applications and preferences
    # For now, just get active jobs that the student hasn't applied to
    applied_jobs = [app.job_listing_id for app in applications]
    recommended_jobs = JobListing.query.filter(
        JobListing.is_active == True,
        ~JobListing.id.in_(applied_jobs) if applied_jobs else True
    ).order_by(JobListing.created_at.desc()).limit(6).all()
    
    return render_template('student_dashboard.html',
                         applications=applications,
                         recommended_jobs=recommended_jobs)

