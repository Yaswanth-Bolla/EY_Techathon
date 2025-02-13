from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.forms import (RegistrationForm, LoginForm)
from flask import Blueprint
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route("/")
def home():
    return render_template('index.html')

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
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        
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
    

    return render_template('student_dashboard.html')

