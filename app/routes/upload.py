from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import pandas as pd
import uuid
import os
from app.models import User, Department, Facility, db
from app.routes.admin import admin_required

bp = Blueprint('upload', __name__)

# Store upload jobs status
upload_jobs = {}

def validate_users_csv(df):
    """Validate users CSV data"""
    errors = []
    
    # Check required columns
    required_columns = ['email', 'name', 'role', 'department_id']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    if not errors:
        # Validate email format
        invalid_emails = df[~df['email'].str.contains('@', na=False)]['email'].tolist()
        if invalid_emails:
            errors.append(f"Invalid email format: {', '.join(invalid_emails)}")
        
        # Validate roles
        valid_roles = ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN', 'USER']
        invalid_roles = df[~df['role'].isin(valid_roles)]['role'].unique().tolist()
        if invalid_roles:
            errors.append(f"Invalid roles: {', '.join(invalid_roles)}")
        
        # Validate department IDs
        existing_dept_ids = {dept.id for dept in Department.query.all()}
        invalid_dept_ids = df[~df['department_id'].isin(existing_dept_ids)]['department_id'].unique().tolist()
        if invalid_dept_ids:
            errors.append(f"Invalid department IDs: {', '.join(map(str, invalid_dept_ids))}")
    
    return errors

def validate_departments_csv(df):
    """Validate departments CSV data"""
    errors = []
    
    # Check required columns
    required_columns = ['name', 'head_id', 'parent_department_id']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    if not errors:
        # Check for duplicate department names
        duplicates = df[df['name'].duplicated()]['name'].tolist()
        if duplicates:
            errors.append(f"Duplicate department names: {', '.join(duplicates)}")
        
        # Validate head_id references
        existing_user_ids = {user.id for user in User.query.all()}
        invalid_head_ids = df[~df['head_id'].isin(existing_user_ids)]['head_id'].unique().tolist()
        if invalid_head_ids:
            errors.append(f"Invalid head IDs: {', '.join(map(str, invalid_head_ids))}")
        
        # Validate parent_department_id references
        existing_dept_ids = {dept.id for dept in Department.query.all()}
        invalid_parent_ids = df[
            (df['parent_department_id'].notna()) & 
            (~df['parent_department_id'].isin(existing_dept_ids))
        ]['parent_department_id'].unique().tolist()
        if invalid_parent_ids:
            errors.append(f"Invalid parent department IDs: {', '.join(map(str, invalid_parent_ids))}")
    
    return errors

def validate_facilities_csv(df):
    """Validate facilities CSV data"""
    errors = []
    
    # Check required columns
    required_columns = ['name', 'department_id', 'description']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    if not errors:
        # Validate department_id references
        existing_dept_ids = {dept.id for dept in Department.query.all()}
        invalid_dept_ids = df[~df['department_id'].isin(existing_dept_ids)]['department_id'].unique().tolist()
        if invalid_dept_ids:
            errors.append(f"Invalid department IDs: {', '.join(map(str, invalid_dept_ids))}")
    
    return errors

@bp.route('/api/upload/csv/users', methods=['POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def upload_users():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
        
        # Validate data
        errors = validate_users_csv(df)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        upload_jobs[job_id] = {'status': 'processing', 'progress': 0}
        
        # Process users
        for _, row in df.iterrows():
            user = User(
                username=row['name'],
                email=row['email'],
                role=row['role'],
                department_id=row['department_id']
            )
            user.set_password('temp_password')  # Set temporary password
            db.session.add(user)
        
        db.session.commit()
        upload_jobs[job_id]['status'] = 'completed'
        
        return jsonify({
            'message': 'Users uploaded successfully',
            'job_id': job_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/upload/csv/departments', methods=['POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def upload_departments():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
        
        # Validate data
        errors = validate_departments_csv(df)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        upload_jobs[job_id] = {'status': 'processing', 'progress': 0}
        
        # Process departments
        for _, row in df.iterrows():
            department = Department(
                name=row['name'],
                description=row.get('description'),
                head_id=row['head_id'],
                parent_id=row['parent_department_id']
            )
            db.session.add(department)
        
        db.session.commit()
        upload_jobs[job_id]['status'] = 'completed'
        
        return jsonify({
            'message': 'Departments uploaded successfully',
            'job_id': job_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/upload/csv/facilities', methods=['POST'])
@login_required
@admin_required(['MASTER_ADMIN', 'ORG_ADMIN'])
def upload_facilities():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
        
        # Validate data
        errors = validate_facilities_csv(df)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        upload_jobs[job_id] = {'status': 'processing', 'progress': 0}
        
        # Process facilities
        for _, row in df.iterrows():
            facility = Facility(
                name=row['name'],
                description=row['description'],
                department_id=row['department_id'],
                type=row.get('type', 'OFFICE'),
                capacity=row.get('capacity'),
                location=row.get('location')
            )
            db.session.add(facility)
        
        db.session.commit()
        upload_jobs[job_id]['status'] = 'completed'
        
        return jsonify({
            'message': 'Facilities uploaded successfully',
            'job_id': job_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/upload/status/<job_id>', methods=['GET'])
@login_required
def get_upload_status(job_id):
    job = upload_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job), 200
