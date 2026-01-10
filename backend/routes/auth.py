"""
Authentication routes for user registration, login, and logout.
Handles session management and password security.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with validation and duplicate email check"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            password = data.get('password', '')
            
            # Validation
            if not all([name, email, phone, password]):
                return jsonify({'error': 'All fields are required'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if user exists
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 409
            
            # Create user
            user = User(name=name, email=email, phone=phone)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': 'Registration successful'}), 201
            else:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Registration failed'}), 500
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with credential verification and session creation"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email and password required'}), 400
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=True)
                
                if request.is_json:
                    return jsonify({
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'is_admin': user.is_admin
                        }
                    }), 200
                else:
                    if user.is_admin:
                        return redirect(url_for('admin.dashboard'))
                    else:
                        return redirect(url_for('user.dashboard'))
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Login failed'}), 500
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout with session cleanup"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))