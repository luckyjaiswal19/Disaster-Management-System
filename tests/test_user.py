import pytest
from extensions import db
from models import User, Resource, Event

def login(client, email, password):
    return client.post('/auth/login', json={
        'email': email,
        'password': password
    }, follow_redirects=True)

def test_user_dashboard_access(client, app):
    """Test that authenticated users can access dashboard"""
    login(client, 'john@example.com', 'password123')
    
    response = client.get('/user/dashboard')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_make_donation(client, app):
    """Test donation creation"""
    login(client, 'john@example.com', 'password123')
    
    with app.app_context():
        resource = Resource.query.first()
        
        response = client.post('/user/donate', json={
            'resource_id': resource.id,
            'quantity': 10,
            'event_id': None,
            'notes': 'Test donation'
        })
        
        assert response.status_code == 201
        assert b'Donation successful' in response.data

def test_create_request(client, app):
    """Test resource request creation"""
    login(client, 'john@example.com', 'password123')
    
    with app.app_context():
        resource = Resource.query.first()
        event = Event.query.first()
        
        response = client.post('/user/requests', json={
            'resource_id': resource.id,
            'event_id': event.id,
            'quantity': 5,
            'urgency': 'Medium'
        })
        
        assert response.status_code == 201
        assert b'Request submitted successfully' in response.data