from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import User, Department, Resource, db
from app.routes.admin import admin_required

bp = Blueprint('users', __name__)

@bp.route('/api/users/<int:user_id>/profile', methods=['GET'])
@login_required
def get_user_profile(user_id):
    # Users can only view their own profile unless they're admins
    if current_user.id != user_id and current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@bp.route('/api/users/<int:user_id>/profile', methods=['PUT'])
@login_required
def update_user_profile(user_id):
    # Users can only update their own profile unless they're admins
    if current_user.id != user_id and current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN']:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.form.to_dict()
    
    # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            user.profile_image = filename
    
    # Update other fields
    allowed_fields = ['username', 'email']
    if current_user.role in ['MASTER_ADMIN', 'ORG_ADMIN']:
        allowed_fields.extend(['role', 'department_id', 'manager_id'])
    
    for key, value in data.items():
        if key in allowed_fields and hasattr(user, key):
            setattr(user, key, value)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@bp.route('/api/users/<int:user_id>/hierarchy', methods=['GET'])
@login_required
def get_user_hierarchy(user_id):
    user = User.query.get_or_404(user_id)
    
    # Build the reporting chain
    reporting_chain = []
    current = user
    while current.manager_id:
        current = current.manager
        reporting_chain.append(current.to_dict())
    
    # Get department information
    department = user.department
    department_head = department.head if department else None
    
    # Get subordinates if user is a manager
    subordinates = [sub.to_dict() for sub in user.subordinates]
    
    return jsonify({
        'user': user.to_dict(),
        'reporting_chain': reporting_chain,
        'department': department.to_dict() if department else None,
        'department_head': department_head.to_dict() if department_head else None,
        'subordinates': subordinates
    }), 200

@bp.route('/api/users/<int:user_id>/resources', methods=['GET'])
@login_required
def get_user_resources(user_id):
    if current_user.id != user_id and current_user.role not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN']:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Get assigned resources
    resources = Resource.query.filter_by(assigned_user_id=user_id).all()
    
    # Get department facilities
    department = user.department
    facilities = department.facilities if department else []
    
    return jsonify({
        'resources': [resource.to_dict() for resource in resources],
        'facilities': [facility.to_dict() for facility in facilities]
    }), 200

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
