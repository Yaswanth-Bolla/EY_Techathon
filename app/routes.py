from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Department, Resource
from app.forms import RegistrationForm, LoginForm
from app.forms import UpdateUserForm, DepartmentForm, ResourceForm, CSVUploadForm
from flask import Blueprint
from datetime import datetime
import csv
import io
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

@bp.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@bp.route("/")
def home():
    return render_template('index.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='USER',  # Only regular users can register
            department_id=form.department.data,
            manager_id=form.manager.data,
            join_date=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            # app.logger.error(f"Error creating user: {str(e)}")
    
    return render_template('register.html', title='Register', form=form)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@bp.route("/dashboard")
@login_required
def dashboard():
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'department': current_user.department.name if current_user.department else 'No Department',
        'manager': current_user.manager.username if current_user.manager else 'No Manager',
        'is_manager': bool(User.query.filter_by(manager_id=current_user.id).first())
    }

    # Get department details
    if current_user.department:
        dept = current_user.department
        user_data['department_head'] = dept.head.username if dept.head else 'No Head'
        user_data['department_description'] = dept.description
        user_data['department_members'] = len(dept.users)

    # Get available resources
    resources_query = Resource.query
    if current_user.role == 'MASTER_ADMIN':
        resources = resources_query.all()
    elif current_user.role == 'ORG_ADMIN':
        dept_ids = [d.id for d in Department.query.filter_by(parent_id=current_user.department_id).all()]
        resources = resources_query.filter(Resource.department_id.in_([current_user.department_id] + dept_ids)).all()
    else:
        resources = resources_query.filter_by(department_id=current_user.department_id).all()

    # Get team members if user is a manager
    team_members = []
    if user_data['is_manager']:
        team_members = User.query.filter_by(manager_id=current_user.id).all()

    # Get assigned resources
    assigned_resources = Resource.query.filter_by(assigned_to_id=current_user.id).all()

    return render_template('dashboard.html', 
                         title='Dashboard',
                         user_data=user_data,
                         resources=resources,
                         team_members=team_members,
                         assigned_resources=assigned_resources)

@bp.route("/manage/users")
@login_required
def manage_users():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    users = []
    if current_user.role == 'MASTER_ADMIN':
        users = User.query.all()
    elif current_user.role == 'ORG_ADMIN':
        dept_ids = [d.id for d in Department.query.filter_by(parent_id=current_user.department_id).all()]
        users = User.query.filter(User.department_id.in_([current_user.department_id] + dept_ids)).all()
    else:  # DEPT_ADMIN
        users = User.query.filter_by(department_id=current_user.department_id).all()
    
    return render_template('admin/manage_users.html', 
                         title='Manage Users',
                         users=users)

@bp.route("/manage/departments")
@login_required
def manage_departments():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    departments = []
    if current_user.role == 'MASTER_ADMIN':
        departments = Department.query.all()
    else:  # ORG_ADMIN
        departments = Department.query.filter(
            (Department.id == current_user.department_id) |
            (Department.parent_id == current_user.department_id)
        ).all()
    
    form = DepartmentForm()
    return render_template('admin/manage_departments.html', 
                         title='Manage Departments',
                         departments=departments,
                         form=form)

@bp.route("/manage/resources")
@login_required
def manage_resources():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    resources = []
    if current_user.role == 'MASTER_ADMIN':
        resources = Resource.query.all()
    elif current_user.role == 'ORG_ADMIN':
        dept_ids = [d.id for d in Department.query.filter_by(parent_id=current_user.department_id).all()]
        resources = Resource.query.filter(Resource.department_id.in_([current_user.department_id] + dept_ids)).all()
    else:  # DEPT_ADMIN
        resources = Resource.query.filter_by(department_id=current_user.department_id).all()
    
    form = ResourceForm()
    return render_template('admin/manage_resources.html', 
                         title='Manage Resources',
                         resources=resources,
                         form=form)

@bp.route("/user/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UpdateUserForm(original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if current_user.role == 'MASTER_ADMIN':
            user.role = form.role.data
        user.department_id = form.department.data
        db.session.commit()
        flash('User has been updated!', 'success')
        return redirect(url_for('main.manage_users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        if hasattr(form, 'role'):
            form.role.data = user.role
        form.department.data = user.department_id
    
    return render_template('admin/edit_user.html', 
                         title='Edit User',
                         form=form,
                         user=user)

@bp.route("/department/<int:dept_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    department = Department.query.get_or_404(dept_id)
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        department.head_id = form.head.data
        if current_user.role == 'MASTER_ADMIN':
            department.parent_id = form.parent.data
        db.session.commit()
        flash('Department has been updated!', 'success')
        return redirect(url_for('main.manage_departments'))
    
    elif request.method == 'GET':
        form.name.data = department.name
        form.description.data = department.description
        form.head.data = department.head_id
        if hasattr(form, 'parent'):
            form.parent.data = department.parent_id
    
    return render_template('admin/edit_department.html', 
                         title='Edit Department',
                         form=form,
                         department=department)

@bp.route("/resource/<int:resource_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    resource = Resource.query.get_or_404(resource_id)
    form = ResourceForm()
    
    if form.validate_on_submit():
        resource.name = form.name.data
        resource.type = form.type.data
        resource.status = form.status.data
        resource.assigned_to_id = form.assigned_to.data
        db.session.commit()
        flash('Resource has been updated!', 'success')
        return redirect(url_for('main.manage_resources'))
    
    elif request.method == 'GET':
        form.name.data = resource.name
        form.type.data = resource.type
        form.status.data = resource.status
        form.assigned_to.data = resource.assigned_to_id
    
    return render_template('admin/edit_resource.html', 
                         title='Edit Resource',
                         form=form,
                         resource=resource)

@bp.route("/resource/add", methods=['GET', 'POST'])
@login_required
def add_resource():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = ResourceForm()
    
    if form.validate_on_submit():
        resource = Resource(
            name=form.name.data,
            type=form.type.data,
            status=form.status.data,
            assigned_to_id=form.assigned_to.data if form.assigned_to.data != 0 else None,
            department_id=current_user.department_id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource has been added!', 'success')
        return redirect(url_for('main.manage_resources'))
    
    return render_template('admin/edit_resource.html', 
                         title='Add Resource',
                         form=form,
                         resource=None)

@bp.route("/department/add", methods=['GET', 'POST'])
@login_required
def add_department():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(
            name=form.name.data,
            description=form.description.data,
            head_id=form.head.data if form.head.data != 0 else None,
            parent_id=form.parent.data if form.parent.data != 0 else None
        )
        db.session.add(department)
        db.session.commit()
        flash('Department has been added!', 'success')
        return redirect(url_for('main.manage_departments'))
    
    return render_template('admin/edit_department.html', 
                         title='Add Department',
                         form=form,
                         department=None)

@bp.route("/user/add", methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = UpdateUserForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash('defaultpassword').decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data if current_user.role == 'MASTER_ADMIN' else 'REGULAR_USER',
            department_id=form.department.data if form.department.data != 0 else None
        )
        db.session.add(user)
        db.session.commit()
        flash('User has been added! Default password is: defaultpassword', 'success')
        return redirect(url_for('main.manage_users'))
    
    return render_template('admin/edit_user.html', 
                         title='Add User',
                         form=form,
                         user=None)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@bp.route("/upload/csv", methods=['GET', 'POST'])
@login_required
def upload_csv():
    if current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CSVUploadForm()
    if form.validate_on_submit():
        if form.file.data:
            try:
                # Read CSV file
                stream = io.StringIO(form.file.data.stream.read().decode("UTF8"), newline=None)
                csv_data = csv.DictReader(stream)
                
                if form.upload_type.data == 'users':
                    for row in csv_data:
                        # Check if user already exists
                        if not User.query.filter_by(email=row['email']).first():
                            hashed_password = bcrypt.generate_password_hash('defaultpassword').decode('utf-8')
                            user = User(
                                username=row['username'],
                                email=row['email'],
                                password=hashed_password,
                                role=row.get('role', 'REGULAR_USER'),
                                department_id=int(row['department_id']) if row.get('department_id') else None
                            )
                            db.session.add(user)
                
                elif form.upload_type.data == 'departments':
                    for row in csv_data:
                        if not Department.query.filter_by(name=row['name']).first():
                            department = Department(
                                name=row['name'],
                                description=row.get('description', ''),
                                head_id=int(row['head_id']) if row.get('head_id') else None,
                                parent_id=int(row['parent_id']) if row.get('parent_id') else None
                            )
                            db.session.add(department)
                
                elif form.upload_type.data == 'resources':
                    for row in csv_data:
                        if not Resource.query.filter_by(name=row['name'], department_id=int(row['department_id'])).first():
                            resource = Resource(
                                name=row['name'],
                                type=row['type'],
                                status=row.get('status', 'available'),
                                department_id=int(row['department_id']),
                                assigned_to_id=int(row['assigned_to_id']) if row.get('assigned_to_id') else None
                            )
                            db.session.add(resource)
                
                db.session.commit()
                flash(f'Successfully uploaded {form.upload_type.data} data!', 'success')
                return redirect(url_for('main.dashboard'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing CSV file: {str(e)}', 'danger')
                return redirect(url_for('main.upload_csv'))
    
    return render_template('admin/upload_csv.html', 
                         title='Upload CSV',
                         form=form)
