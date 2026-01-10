import pytest
from extensions import db
from models import User

def test_register_success(client, app):
    """Test successful user registration"""
    with app.app_context():
        response = client.post('/auth/register', json={
            'name': 'New User',
            'email': 'new@example.com',
            'phone': '+1234567800',
            'password': 'testpass123'
        })
        
        assert response.status_code == 201
        assert b'Registration successful' in response.data
        
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        assert user.name == 'New User'

def test_register_duplicate_email(client, app):
    """Test registration with duplicate email"""
    with app.app_context():
        # John Doe is already seeded in conftest
        response = client.post('/auth/register', json={
            'name': 'Second User',
            'email': 'john@example.com',
            'phone': '+1234567892',
            'password': 'testpass123'
        })
        
        assert response.status_code == 409
        assert b'Email already registered' in response.data

def test_login_success(client, app):
    """Test successful user login"""
    with app.app_context():
        # Use seeded user
        response = client.post('/auth/login', json={
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Login successful' in response.data

def test_login_invalid_credentials(client, app):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', json={
        'email': 'john@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert b'Invalid email or password' in response.data