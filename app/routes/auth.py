from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import jwt
from app.models import User, db

bp = Blueprint('auth', __name__)

def generate_token(user_id):
    """Generate JWT token for the user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

@bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user, remember=data.get('remember', False))
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'token': generate_token(user.id),
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out'}), 200

@bp.route('/api/auth/refresh-token', methods=['POST'])
@login_required
def refresh_token():
    return jsonify({
        'token': generate_token(current_user.id)
    }), 200

@bp.route('/api/auth/user-profile', methods=['GET'])
@login_required
def get_user_profile():
    return jsonify(current_user.to_dict()), 200

@bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    if data['role'] not in ['MASTER_ADMIN', 'ORG_ADMIN', 'DEPT_ADMIN', 'USER']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role'],
        department_id=data.get('department_id'),
        manager_id=data.get('manager_id')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201
