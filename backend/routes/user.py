"""
User-facing routes for dashboard, donations, requests, and map interactions.
Provides relief coordination functionality for regular users.
"""
from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Event, Resource, Donation, Request
from sqlalchemy.exc import SQLAlchemyError
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing events, resources, donations, and requests"""
    events = Event.query.filter_by(status='Active').all()
    resources = Resource.query.all()
    donations = Donation.query.filter_by(user_id=current_user.id).order_by(Donation.donated_at.desc()).limit(10).all()
    requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).limit(10).all()
    
    return render_template('user_dashboard.html',
                         events=events,
                         resources=resources,
                         donations=donations,
                         requests=requests)

@user_bp.route('/events')
@login_required
def get_events():
    """API endpoint for events data (used by map)"""
    events = Event.query.filter_by(status='Active').all()
    events_data = [{
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'latitude': event.latitude,
        'longitude': event.longitude,
        'severity': event.severity
    } for event in events]
    
    return jsonify(events_data)

@user_bp.route('/resources')
@login_required
def get_resources():
    """API endpoint for resources data"""
    resources = Resource.query.all()
    resources_data = [{
        'id': resource.id,
        'name': resource.name,
        'category': resource.category,
        'available_quantity': resource.available_quantity,
        'unit': resource.unit
    } for resource in resources]
    
    return jsonify(resources_data)

@user_bp.route('/donate', methods=['POST'])
@login_required
def donate():
    """Create a donation with transaction handling and quantity updates"""
    try:
        data = request.get_json() if request.is_json else request.form
        resource_id = data.get('resource_id')
        quantity = data.get('quantity')
        event_id = data.get('event_id')
        notes = data.get('notes', '')
        
        if not resource_id or not quantity:
            return jsonify({'error': 'Resource and quantity are required'}), 400
        
        try:
            resource_id = int(resource_id)
            quantity = int(quantity)
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid quantity format'}), 400
        
        # Start transaction
        db.session.begin_nested()
        
        # Check resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            db.session.rollback()
            return jsonify({'error': 'Resource not found'}), 404
        
        # Create donation
        donation = Donation(
            user_id=current_user.id,
            resource_id=resource_id,
            event_id=event_id,
            quantity=quantity,
            notes=notes
        )
        
        db.session.add(donation)
        
        # Update resource quantities (trigger will handle this, but we do it here too for consistency)
        resource.total_quantity += quantity
        resource.available_quantity += quantity
        
        db.session.commit()
        
        return jsonify({
            'message': 'Donation successful',
            'donation_id': donation.id
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Donation failed due to database error'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Donation failed'}), 500

@user_bp.route('/requests', methods=['POST'])
@login_required
def create_request():
    """Create resource request with availability validation"""
    try:
        data = request.get_json() if request.is_json else request.form
        resource_id = data.get('resource_id')
        event_id = data.get('event_id')
        quantity = data.get('quantity')
        urgency = data.get('urgency', 'Medium')
        
        if not all([resource_id, event_id, quantity]):
            return jsonify({'error': 'Resource, event, and quantity are required'}), 400
        
        try:
            resource_id = int(resource_id)
            event_id = int(event_id)
            quantity = int(quantity)
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid input format'}), 400
        
        # Check resource and event exist
        resource = Resource.query.get(resource_id)
        event = Event.query.get(event_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Create request (availability check happens in trigger)
        request_obj = Request(
            user_id=current_user.id,
            resource_id=resource_id,
            event_id=event_id,
            quantity=quantity,
            urgency=urgency
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        return jsonify({
            'message': 'Request submitted successfully',
            'request_id': request_obj.id
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Request creation failed'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Request creation failed'}), 500

@user_bp.route('/requests/<int:request_id>')
@login_required
def get_request(request_id):
    """Get specific request details with authorization check"""
    request_obj = Request.query.filter_by(id=request_id, user_id=current_user.id).first()
    if not request_obj:
        return jsonify({'error': 'Request not found'}), 404
    
    request_data = {
        'id': request_obj.id,
        'resource_name': request_obj.resource.name,
        'event_name': request_obj.event.name,
        'quantity': request_obj.quantity,
        'urgency': request_obj.urgency,
        'status': request_obj.status,
        'created_at': request_obj.created_at.isoformat()
    }
    
    # Add response data if exists
    if request_obj.responses:
        response = request_obj.responses[0]
        request_data['response'] = {
            'action': response.action,
            'comment': response.comment,
            'responded_at': response.responded_at.isoformat(),
            'admin_name': response.admin.name
        }
    
    return jsonify(request_data)