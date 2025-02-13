from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for team members
team_members = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_team_member_user'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id', use_alter=True, name='fk_team_member_team'), primary_key=True),
    db.Column('joined_at', db.DateTime, nullable=False, default=datetime.utcnow)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', use_alter=True, name='fk_user_department'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_user_manager'), nullable=True)
    profile_image = db.Column(db.String(20), nullable=True, default='default.jpg')
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    current_project_id = db.Column(db.Integer, db.ForeignKey('project.id', use_alter=True, name='fk_user_project'), nullable=True)

    # Relationships
    department = db.relationship('Department', foreign_keys=[department_id], back_populates='users')
    manager = db.relationship('User', remote_side=[id], backref=db.backref('subordinates', lazy='dynamic'), foreign_keys=[manager_id])
    managed_departments = db.relationship('Department', back_populates='head', foreign_keys='Department.head_id')
    resources = db.relationship('Resource', backref='assigned_user', foreign_keys='Resource.assigned_to_id')
    current_project = db.relationship('Project', foreign_keys=[current_project_id])
    # Team relationships
    member_of_teams = db.relationship('Team', secondary=team_members, back_populates='team_members')
    led_teams = db.relationship('Team', backref='team_leader', foreign_keys='Team.leader_id')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

    def set_password(self, password):
        from app import bcrypt
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    head_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_department_head'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('department.id', use_alter=True, name='fk_department_parent'), nullable=True)
    department_type = db.Column(db.String(20), nullable=False, default='department')  # 'department', 'subdepartment'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', foreign_keys='User.department_id', back_populates='department')
    head = db.relationship('User', foreign_keys=[head_id], back_populates='managed_departments')
    parent = db.relationship('Department', remote_side=[id], backref=db.backref('sub_departments', lazy='dynamic'))
    teams = db.relationship('Team', backref='department', lazy='dynamic')
    processes = db.relationship('Process', backref='department')

    def __repr__(self):
        return f"Department('{self.name}', Type: '{self.department_type}')"

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', use_alter=True, name='fk_team_department'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_team_leader'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    team_members = db.relationship('User', secondary=team_members, back_populates='member_of_teams')
    projects = db.relationship('Project', backref='team', lazy='dynamic')

    def __repr__(self):
        return f"Team('{self.name}')"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', use_alter=True, name='fk_project_team'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'completed', 'on_hold'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Project('{self.name}', Status: '{self.status}')"

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default='available')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    rto_hours = db.Column(db.Integer)  # Recovery Time Objective in hours
    criticality_level = db.Column(db.String(20))  # Low, Medium, High, Critical
    
    # Relationships
    internal_dependencies = db.relationship('InternalDependency', backref='process', lazy='dynamic')
    external_dependencies = db.relationship('ExternalDependency', backref='process', lazy='dynamic')
    inputs = db.relationship('ProcessInput', backref='process', lazy='dynamic')
    outputs = db.relationship('ProcessOutput', backref='process', lazy='dynamic')
    impact_assessment = db.relationship('ImpactAssessment', backref='process', uselist=False)

    def __repr__(self):
        return f'<Process {self.name}>'

class InternalDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    dependent_department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    description = db.Column(db.Text)

class ExternalDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    service_description = db.Column(db.Text)
    contact_info = db.Column(db.String(200))

class ProcessInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50))  # Data, Document, Tool, etc.

class ProcessOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deliverable_type = db.Column(db.String(50))

class ProcessStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)

class ImpactAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    financial_impact = db.Column(db.Integer)  # 0-4 scale
    operational_impact = db.Column(db.Integer)  # 0-4 scale
    legal_impact = db.Column(db.Integer)  # 0-4 scale
    reputational_impact = db.Column(db.Integer)  # 0-4 scale
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class VitalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    system = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    required_resources = db.Column(db.Text)

class MinimumOperatingRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'), nullable=False)
    requirement_type = db.Column(db.String(50))  # IT, Software, Equipment
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    specifications = db.Column(db.Text)
