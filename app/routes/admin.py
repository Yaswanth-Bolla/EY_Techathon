from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Department, Resource, Facility, db

bp = Blueprint('admin', __name__)

def admin_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in role:
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/api/admin/dashboard', methods=['GET'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def get_dashboard():
    total_users = User.query.count()
    total_departments = Department.query.count()
    total_resources = Resource.query.count()
    total_facilities = Facility.query.count()
    
    return jsonify({
        'statistics': {
            'total_users': total_users,
            'total_departments': total_departments,
            'total_resources': total_resources,
            'total_facilities': total_facilities
        }
    }), 200

@bp.route('/api/admin/departments', methods=['GET', 'POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def manage_departments():
    if request.method == 'GET':
        departments = Department.query.all()
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Department name is required'}), 400
    
    department = Department(
        name=data['name'],
        description=data.get('description'),
        head_id=data.get('head_id'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(department)
    db.session.commit()
    
    return jsonify({
        'message': 'Department created successfully',
        'department': department.to_dict()
    }), 201

@bp.route('/api/admin/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def manage_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    
    if request.method == 'DELETE':
        db.session.delete(department)
        db.session.commit()
        return jsonify({'message': 'Department deleted successfully'}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    department.name = data.get('name', department.name)
    department.description = data.get('description', department.description)
    department.head_id = data.get('head_id', department.head_id)
    department.parent_id = data.get('parent_id', department.parent_id)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Department updated successfully',
        'department': department.to_dict()
    }), 200

@bp.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def get_users():
    if current_user.role == 'DEPT_ADMIN':
        users = User.query.filter_by(department_id=current_user.department_id).all()
    else:
        users = User.query.all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@bp.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def manage_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'role' in data and data['role'] not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN', 'USER']:
        return jsonify({'error': 'Invalid role'}), 400
    
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@bp.route('/api/admin/audit-logs', methods=['GET'])
@login_required
@admin_required(['MASTER_ADMIN'])
def get_audit_logs():
    # This would typically integrate with a logging system
    return jsonify({
        'message': 'Audit logs functionality to be implemented'
    }), 200
