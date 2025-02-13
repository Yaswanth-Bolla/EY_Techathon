from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Resource, Facility, Department, db
from app.routes.admin import admin_required

bp = Blueprint('resources', __name__)

@bp.route('/api/resources', methods=['GET'])
@login_required
def get_resources():
    if current_user.role == 'MASTER_ADMIN':
        resources = Resource.query.all()
    elif current_user.role in ['ORG_ADMIN', 'DEPT_ADMIN']:
        dept_ids = [dept.id for dept in Department.query.all()] if current_user.role == 'ORG_ADMIN' else [current_user.department_id]
        resources = Resource.query.filter(Resource.department_id.in_(dept_ids)).all()
    else:
        resources = Resource.query.filter_by(department_id=current_user.department_id).all()
    
    return jsonify({
        'resources': [resource.to_dict() for resource in resources]
    }), 200

@bp.route('/api/resources', methods=['POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def create_resource():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'type', 'department_id']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user has permission for the department
    if current_user.role == 'DEPT_ADMIN' and data['department_id'] != current_user.department_id:
        return jsonify({'error': 'Unauthorized to create resource for this department'}), 403
    
    resource = Resource(
        name=data['name'],
        type=data['type'],
        department_id=data['department_id'],
        status=data.get('status', 'available')
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({
        'message': 'Resource created successfully',
        'resource': resource.to_dict()
    }), 201

@bp.route('/api/resources/<int:resource_id>', methods=['PUT'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def update_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    # Check permission
    if current_user.role == 'DEPT_ADMIN' and resource.department_id != current_user.department_id:
        return jsonify({'error': 'Unauthorized to modify this resource'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    for key, value in data.items():
        if hasattr(resource, key):
            setattr(resource, key, value)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Resource updated successfully',
        'resource': resource.to_dict()
    }), 200

@bp.route('/api/resources/<int:resource_id>', methods=['DELETE'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    # Check permission
    if current_user.role == 'DEPT_ADMIN' and resource.department_id != current_user.department_id:
        return jsonify({'error': 'Unauthorized to delete this resource'}), 403
    
    db.session.delete(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource deleted successfully'}), 200

@bp.route('/api/facilities', methods=['GET'])
@login_required
def get_facilities():
    if current_user.role == 'MASTER_ADMIN':
        facilities = Facility.query.all()
    elif current_user.role in ['ORG_ADMIN', 'DEPT_ADMIN']:
        dept_ids = [dept.id for dept in Department.query.all()] if current_user.role == 'ORG_ADMIN' else [current_user.department_id]
        facilities = Facility.query.filter(Facility.department_id.in_(dept_ids)).all()
    else:
        facilities = Facility.query.filter_by(department_id=current_user.department_id).all()
    
    return jsonify({
        'facilities': [facility.to_dict() for facility in facilities]
    }), 200

@bp.route('/api/facilities', methods=['POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def create_facility():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'type', 'department_id']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user has permission for the department
    if current_user.role == 'DEPT_ADMIN' and data['department_id'] != current_user.department_id:
        return jsonify({'error': 'Unauthorized to create facility for this department'}), 403
    
    facility = Facility(
        name=data['name'],
        type=data['type'],
        capacity=data.get('capacity'),
        location=data.get('location'),
        department_id=data['department_id'],
        status=data.get('status', 'available')
    )
    
    db.session.add(facility)
    db.session.commit()
    
    return jsonify({
        'message': 'Facility created successfully',
        'facility': facility.to_dict()
    }), 201

@bp.route('/api/facilities/<int:facility_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN'])
def manage_facility(facility_id):
    facility = Facility.query.get_or_404(facility_id)
    
    # Check permission
    if current_user.role == 'DEPT_ADMIN' and facility.department_id != current_user.department_id:
        return jsonify({'error': 'Unauthorized to modify this facility'}), 403
    
    if request.method == 'DELETE':
        db.session.delete(facility)
        db.session.commit()
        return jsonify({'message': 'Facility deleted successfully'}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    for key, value in data.items():
        if hasattr(facility, key):
            setattr(facility, key, value)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Facility updated successfully',
        'facility': facility.to_dict()
    }), 200
