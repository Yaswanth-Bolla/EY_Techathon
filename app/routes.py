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

@bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    students = User.query.filter_by(role='student').all()
    companies = Company.query.all()
    pending_companies = Company.query.filter_by(is_approved=False).all()
    jobs = JobListing.query.order_by(JobListing.created_at.desc()).all()
    applications = JobApplication.query.order_by(JobApplication.date_of_application.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         students=students,
                         companies=companies,
                         pending_companies=pending_companies,
                         jobs=jobs,
                         applications=applications)

@bp.route("/company_dashboard")
@login_required
def company_dashboard():
    if current_user.role != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        flash('Company profile not found', 'danger')
        return redirect(url_for('main.home'))
    
    job_listings = JobListing.query.filter_by(company_id=company.id).order_by(JobListing.created_at.desc()).all()
    applications = JobApplication.query.filter_by(company_id=company.id).order_by(JobApplication.date_of_application.desc()).all()
    
    return render_template('company_dashboard.html',
                         company=company,
                         job_listings=job_listings,
                         applications=applications)

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

@bp.route("/approve_company/<int:company_id>", methods=['POST'])
@login_required
def approve_company(company_id):
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    
    flash('Company has been approved!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@bp.route("/reject_company/<int:company_id>", methods=['POST'])
@login_required
def reject_company(company_id):
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    
    flash('Company has been rejected and removed.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@bp.route("/post_job", methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company or not company.is_approved:
        flash('Your company needs to be approved before posting jobs', 'warning')
        return redirect(url_for('main.company_dashboard'))
    
    form = JobListingForm()
    if form.validate_on_submit():
        job = JobListing(
            title=form.title.data,
            description=form.description.data,
            salary_range=form.salary_range.data,
            required_skills=form.required_skills.data,
            category=form.category.data,
            company_id=company.id,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()
        flash('Job listing has been created!', 'success')
        return redirect(url_for('main.company_dashboard'))
    
    return render_template('edit_job.html', title='Post Job', form=form)

@bp.route("/jobs")
def jobs():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = JobListing.query.filter_by(is_active=True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (JobListing.title.ilike(search_term)) |
            (JobListing.description.ilike(search_term)) |
            (JobListing.required_skills.ilike(search_term))
        )
    
    if category:
        query = query.filter_by(category=category)
    
    jobs = query.order_by(JobListing.created_at.desc()).all()
    return render_template('jobs.html', jobs=jobs)

@bp.route("/edit_job/<int:job_id>", methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if current_user.role != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    job = JobListing.query.get_or_404(job_id)
    company = Company.query.filter_by(user_id=current_user.id).first()
    
    if job.company_id != company.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    form = JobListingForm()
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        job.salary_range = form.salary_range.data
        job.required_skills = form.required_skills.data
        job.category = form.category.data
        job.is_active = form.is_active.data
        db.session.commit()
        flash('Job listing has been updated!', 'success')
        return redirect(url_for('main.company_dashboard'))
    elif request.method == 'GET':
        form.title.data = job.title
        form.description.data = job.description
        form.salary_range.data = job.salary_range
        form.required_skills.data = job.required_skills
        form.category.data = job.category
        form.is_active.data = job.is_active
    
    return render_template('edit_job.html', title='Edit Job', form=form, job=job)

@bp.route("/apply_job/<int:job_id>", methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'student':
        flash('Only students can apply for jobs', 'danger')
        return redirect(url_for('main.home'))
    
    job = JobListing.query.get_or_404(job_id)
    if not job.is_active:
        flash('This job is no longer accepting applications', 'warning')
        return redirect(url_for('main.jobs'))
    
    # Check if already applied
    existing_application = JobApplication.query.filter_by(
        student_id=current_user.id,
        job_listing_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job', 'info')
        return redirect(url_for('main.view_application', application_id=existing_application.id))
    
    form = JobApplicationForm()
    if form.validate_on_submit():
        application = JobApplication(
            student_id=current_user.id,
            job_listing_id=job_id,
            company_id=job.company_id,
            resume_link=form.resume_link.data,
            expected_salary=form.expected_salary.data,
            remarks=form.remarks.data,
            status='applied'
        )
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted!', 'success')
        return redirect(url_for('main.student_dashboard'))
    
    return render_template('apply_job.html', title='Apply for Job', form=form, job=job)

@bp.route("/update_application_status/<int:application_id>", methods=['POST'])
@login_required
def update_application_status(application_id):
    if current_user.role != 'company':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    application = JobApplication.query.get_or_404(application_id)
    company = Company.query.filter_by(user_id=current_user.id).first()
    
    if application.company_id != company.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    status = request.form.get('status')
    if status not in ['shortlisted', 'interviewed', 'selected', 'rejected']:
        flash('Invalid status', 'danger')
        return redirect(url_for('main.view_application', application_id=application_id))
    
    application.status = status
    db.session.commit()
    flash(f'Application status updated to {status}', 'success')
    return redirect(url_for('main.view_application', application_id=application_id))

@bp.route("/view_application/<int:application_id>")
@login_required
def view_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    
    # Check permissions
    if current_user.role == 'student' and application.student_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    elif current_user.role == 'company':
        company = Company.query.filter_by(user_id=current_user.id).first()
        if application.company_id != company.id:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.home'))
    
    return render_template('view_application.html', application=application)

@bp.route("/toggle_job_status/<int:job_id>", methods=['POST'])
@login_required
def toggle_job_status(job_id):
    if current_user.role not in ['company', 'admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    
    job = JobListing.query.get_or_404(job_id)
    
    if current_user.role == 'company':
        company = Company.query.filter_by(user_id=current_user.id).first()
        if job.company_id != company.id:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.home'))
    
    job.is_active = not job.is_active
    db.session.commit()
    
    flash(f'Job listing has been {"activated" if job.is_active else "deactivated"}', 'success')
    return redirect(request.referrer or url_for('main.home'))