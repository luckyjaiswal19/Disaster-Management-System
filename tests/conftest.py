import pytest
import sys
import os

# Add backend to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app
from extensions import db
from models import User

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test users
        admin = User(name='Admin User', email='admin@disaster.org', phone='+1234567890', is_admin=True)
        admin.set_password('password123')
        
        user = User(name='John Doe', email='john@example.com', phone='+1234567891')
        user.set_password('password123')
        
        db.session.add(admin)
        db.session.add(user)
        
        # Create test event and resource
        from models import Event, Resource
        event = Event(name='Test Event', description='Test Desc', latitude=0.0, longitude=0.0, severity='Medium')
        resource = Resource(name='Water', category='Food', description='Water', total_quantity=100, available_quantity=100, unit='bottles')
        
        db.session.add(event)
        db.session.add(resource)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
