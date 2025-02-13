from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User, JobListing
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('company', 'Company')])
    
    # Additional fields for companies
    company_name = StringField('Company Name')
    description = TextAreaField('Company Description', default='')
    
    submit = SubmitField('Sign Up')

    def validate(self, extra_validators=None):
        if not super().validate():
            return False
            
        if self.role.data == 'company':
            if not self.company_name.data:
                self.company_name.errors = ['Company name is required']
                return False
            if not self.description.data:
                self.description.errors = ['Company description is required']
                return False
        return True

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
        validators=[DataRequired()])
    submit = SubmitField('Login')

class CompanyProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    industry = SelectField('Industry', 
        choices=[], 
        validators=[DataRequired()])
    description = TextAreaField('Company Description')
    submit = SubmitField('Update Profile')

class JobListingForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    salary_range = StringField('Salary Range', validators=[DataRequired()])
    required_skills = TextAreaField('Required Skills', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('software', 'Software Development'),
        ('data', 'Data Science'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('operations', 'Operations'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Post Job')

class JobApplicationForm(FlaskForm):
    resume_link = StringField('Resume Link', validators=[DataRequired()])
    expected_salary = FloatField('Expected Salary', validators=[DataRequired(), NumberRange(min=0)])
    remarks = TextAreaField('Cover Letter/Additional Notes')
    submit = SubmitField('Submit Application')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', 
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], 
        coerce=int,
        validators=[DataRequired()])
    comment = TextAreaField('Review Comments')
    submit = SubmitField('Submit Review')