"""
Database models using SQLAlchemy ORM.
Defines all tables and relationships with proper constraints and indexes.
"""
from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """
    User model with authentication and role-based access control.
    Supports both regular users and administrators.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_volunteer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='user', lazy=True)
    requests = db.relationship('Request', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Event(db.Model):
    """
    Disaster events with geographic coordinates for map visualization.
    Represents different disaster incidents requiring relief coordination.
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    status = db.Column(db.String(50), default='Active')    # Active, Resolved, Archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='event', lazy=True)
    requests = db.relationship('Request', backref='event', lazy=True)

class Resource(db.Model):
    """
    Relief resources available in the system.
    Tracks quantities and categories for efficient resource management.
    """
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # Food, Medical, Shelter, etc.
    description = db.Column(db.Text)
    total_quantity = db.Column(db.Integer, default=0)
    available_quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='units')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='resource', lazy=True)
    requests = db.relationship('Request', backref='resource', lazy=True)

class Donation(db.Model):
    """
    Donations made by users to support relief efforts.
    Updates resource quantities and can be tied to specific events.
    """
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='SET NULL'), nullable=True, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Completed')  # Pending, Completed, Cancelled
    donated_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class Request(db.Model):
    """
    Resource requests from users for specific disaster events.
    Goes through approval workflow managed by administrators.
    """
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.String(50), default='Medium')  # Low, Medium, High, Critical
    status = db.Column(db.String(50), default='Pending', index=True)  # Pending, Approved, Rejected, Fulfilled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('AdminResponse', backref='request', lazy=True)

class AdminResponse(db.Model):
    """
    Administrative responses to user requests.
    Tracks approval/rejection decisions and administrator comments.
    """
    __tablename__ = 'admin_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # Approved, Rejected
    comment = db.Column(db.Text)
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    admin = db.relationship('User', backref='responses')

class VolunteerAssignment(db.Model):
    """
    Assignments for volunteers to fulfill requests.
    """
    __tablename__ = 'volunteer_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(50), default='Assigned')  # Assigned, In Progress, Completed
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='assignments')
    request_obj = db.relationship('Request', backref='assignments')

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))