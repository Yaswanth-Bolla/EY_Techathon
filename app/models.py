from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

    # Relationships
    department = db.relationship('Department', foreign_keys=[department_id], back_populates='users')
    manager = db.relationship('User', remote_side=[id], backref=db.backref('subordinates', lazy='dynamic'), foreign_keys=[manager_id])
    managed_departments = db.relationship('Department', back_populates='head', foreign_keys='Department.head_id')
    resources = db.relationship('Resource', backref='assigned_user', foreign_keys='Resource.assigned_to_id')

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
    
    # Relationships
    users = db.relationship('User', foreign_keys='User.department_id', back_populates='department')
    head = db.relationship('User', foreign_keys=[head_id], back_populates='managed_departments')
    parent = db.relationship('Department', remote_side=[id], backref=db.backref('sub_departments', lazy='dynamic'))

    def __repr__(self):
        return f"Department('{self.name}')"

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
