from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Department

__all__ = ['LoginForm', 'RegistrationForm', 'UpdateProfileForm', 'UpdateUserForm', 'DepartmentForm', 'ResourceForm', 'FacilityForm', 'CSVUploadForm']

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    manager = SelectField('Manager', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Get all departments
        departments = Department.query.filter_by(parent_id=None).all()  # Get main departments
        self.department.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in departments]
        
        # Get all managers (department admins and org admins)
        managers = User.query.filter(User.role.in_(['DEPT_ADMIN', 'ORG_ADMIN'])).all()
        self.manager.choices = [(0, 'Select Manager')] + [(u.id, f"{u.username} ({u.role})") for u in managers]

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use another one.')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please use a different email.')

class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('REGULAR_USER', 'Regular User'),
        ('DEPT_ADMIN', 'Department Admin'),
        ('ORG_ADMIN', 'Organization Admin')
    ])
    department = SelectField('Department', coerce=int)
    submit = SubmitField('Update User')

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        departments = Department.query.all()
        self.department.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in departments]

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please use a different username.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please use a different email.')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    head = SelectField('Department Head', coerce=int)
    parent = SelectField('Parent Department', coerce=int)
    submit = SubmitField('Save Department')

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        admins = User.query.filter(User.role.in_(['DEPT_ADMIN', 'ORG_ADMIN'])).all()
        self.head.choices = [(0, 'Select Head')] + [(u.id, f"{u.username} ({u.role})") for u in admins]
        departments = Department.query.all()
        self.parent.choices = [(0, 'No Parent')] + [(d.id, d.name) for d in departments]

class ResourceForm(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Resource Type', choices=[
        ('HARDWARE', 'Hardware'),
        ('SOFTWARE', 'Software'),
        ('FACILITY', 'Facility'),
        ('OTHER', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired')
    ])
    assigned_to = SelectField('Assigned To', coerce=int)
    submit = SubmitField('Save Resource')

    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        users = User.query.all()
        self.assigned_to.choices = [(0, 'Not Assigned')] + [(u.id, f"{u.username} ({u.department.name if u.department else 'No Department'})") for u in users]

class FacilityForm(FlaskForm):
    name = StringField('Facility Name', validators=[DataRequired(), Length(max=100)])
    type = SelectField('Facility Type', choices=[
        ('OFFICE', 'Office Space'),
        ('MEETING', 'Meeting Room'),
        ('EQUIPMENT', 'Equipment Room'),
        ('PARKING', 'Parking Space')
    ])
    capacity = StringField('Capacity')
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    department = SelectField('Department', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(FacilityForm, self).__init__(*args, **kwargs)
        self.department.choices = [(d.id, d.name) for d in Department.query.all()]

class CSVUploadForm(FlaskForm):
    file = FileField('CSV File', validators=[
        DataRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    upload_type = SelectField('Upload Type', choices=[
        ('users', 'Users'),
        ('departments', 'Departments'),
        ('resources', 'Resources')
    ])
    submit = SubmitField('Upload')
