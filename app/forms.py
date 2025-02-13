from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User, Department

__all__ = ['LoginForm', 'RegistrationForm', 'UpdateProfileForm', 'UpdateUserForm', 'DepartmentForm', 'ResourceForm', 'FacilityForm', 'CSVUploadForm', 'ProcessForm']

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
    department = SelectField('Department', coerce=int)
    subdepartment = SelectField('Sub-Department', coerce=int)
    team = SelectField('Team', coerce=int)
    project = SelectField('Project', coerce=int)
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Get main departments
        departments = Department.query.filter_by(department_type='department', parent_id=None).all()
        self.department.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in departments]
        
        # Initialize other dropdowns with placeholders
        self.subdepartment.choices = [(0, 'Select Department First')]
        self.team.choices = [(0, 'Select Sub-Department First')]
        self.project.choices = [(0, 'Select Team First')]

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use another one.')

    def validate_department(self, department):
        if department.data == 0:
            raise ValidationError('Please select a department.')

    def validate_subdepartment(self, subdepartment):
        if subdepartment.data == 0:
            raise ValidationError('Please select a sub-department.')

    def validate_team(self, team):
        if team.data == 0:
            raise ValidationError('Please select a team.')

    def validate_project(self, project):
        if project.data == 0:
            raise ValidationError('Please select a project.')

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

    def validate_department(self, department):
        if department.data == 0:
            raise ValidationError('Please select a department.')

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

    def validate_head(self, head):
        if head.data == 0:
            raise ValidationError('Please select a department head.')

    def validate_parent(self, parent):
        if parent.data == 0:
            raise ValidationError('Please select a parent department.')

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

    def validate_assigned_to(self, assigned_to):
        if assigned_to.data == 0:
            raise ValidationError('Please select a user to assign the resource to.')

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

    def validate_department(self, department):
        if department.data == 0:
            raise ValidationError('Please select a department.')

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

    def validate_upload_type(self, upload_type):
        if upload_type.data == 0:
            raise ValidationError('Please select an upload type.')

class ProcessForm(FlaskForm):
    name = StringField('Process Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    rto_hours = IntegerField('Recovery Time Objective (hours)', validators=[DataRequired(), NumberRange(min=0)])
    criticality_level = SelectField('Criticality Level',
                                  choices=[('Low', 'Low'),
                                         ('Medium', 'Medium'),
                                         ('High', 'High'),
                                         ('Critical', 'Critical')],
                                  validators=[DataRequired()])
    
    # Impact Assessment
    financial_impact = IntegerField('Financial Impact (0-4)', 
                                  validators=[DataRequired(), NumberRange(min=0, max=4)])
    operational_impact = IntegerField('Operational Impact (0-4)', 
                                    validators=[DataRequired(), NumberRange(min=0, max=4)])
    legal_impact = IntegerField('Legal Impact (0-4)', 
                              validators=[DataRequired(), NumberRange(min=0, max=4)])
    reputational_impact = IntegerField('Reputational Impact (0-4)', 
                                     validators=[DataRequired(), NumberRange(min=0, max=4)])
    impact_notes = TextAreaField('Impact Assessment Notes')
    
    submit = SubmitField('Save Process')

    def __init__(self, *args, **kwargs):
        super(ProcessForm, self).__init__(*args, **kwargs)
        departments = Department.query.all()
        self.department_id.choices = [(d.id, d.name) for d in departments]
