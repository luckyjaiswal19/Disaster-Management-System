"""
Administrative routes for request management and system oversight.
Requires admin privileges and handles critical resource allocation.
"""
from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Event, Resource, Donation, Request, AdminResponse
from sqlalchemy import text
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """Decorator to ensure user has admin privileges"""
    from functools import wraps
    
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview and pending requests"""
    pending_requests = Request.query.filter_by(status='Pending').order_by(Request.created_at.desc()).all()
    resources = Resource.query.all()
    events = Event.query.all()
    recent_donations = Donation.query.order_by(Donation.donated_at.desc()).limit(10).all()
    all_requests = Request.query.order_by(Request.created_at.desc()).limit(10).all()
    
    # Statistics
    stats = {
        'total_users': User.query.count(),
        'total_events': len(events),
        'total_requests': Request.query.count(),
        'pending_requests': len(pending_requests),
        'total_donations': Donation.query.count(),
    }
    
    return render_template('admin_dashboard.html',
                         pending_requests=pending_requests,
                         resources=resources,
                         events=events,
                         donations=recent_donations,
                         all_requests=all_requests,
                         stats=stats)

@admin_bp.route('/requests')
@login_required
@admin_required
def get_requests():
    """API endpoint for all requests with filtering and pagination"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Request.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(Request.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    requests_data = [{
        'id': req.id,
        'user_name': req.user.name,
        'resource_name': req.resource.name,
        'event_name': req.event.name,
        'quantity': req.quantity,
        'urgency': req.urgency,
        'status': req.status,
        'created_at': req.created_at.isoformat()
    } for req in requests.items]
    
    return jsonify({
        'requests': requests_data,
        'total': requests.total,
        'pages': requests.pages,
        'current_page': page
    })

@admin_bp.route('/requests/<int:request_id>/action', methods=['POST'])
@login_required
@admin_required
def process_request(request_id):
    """
    Process request using stored procedure for transaction safety.
    Handles both approval and rejection with proper resource management.
    """
    try:
        data = request.get_json() if request.is_json else request.form
        action = data.get('action')  # 'approve' or 'reject'
        comment = data.get('comment', '')
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Use stored procedure for atomic operation
        if action == 'approve':
            result = db.session.execute(
                text('CALL process_request_approval(:request_id, :admin_id, :comment)'),
                {'request_id': request_id, 'admin_id': current_user.id, 'comment': comment}
            )
            message = 'Request approved successfully'
        else:
            result = db.session.execute(
                text('CALL process_request_rejection(:request_id, :admin_id, :comment)'),
                {'request_id': request_id, 'admin_id': current_user.id, 'comment': comment}
            )
            message = 'Request rejected successfully'
        
        db.session.commit()
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if 'insufficient' in error_msg.lower():
            return jsonify({'error': 'Insufficient resource quantity'}), 400
        elif 'not found' in error_msg.lower():
            return jsonify({'error': 'Request not found'}), 404
        else:
            return jsonify({'error': 'Action failed'}), 500

@admin_bp.route('/resources')
@login_required
@admin_required
def get_resources():
    """API endpoint for resource management"""
    resources = Resource.query.all()
    resources_data = [{
        'id': resource.id,
        'name': resource.name,
        'category': resource.category,
        'total_quantity': resource.total_quantity,
        'available_quantity': resource.available_quantity,
        'unit': resource.unit
    } for resource in resources]
    
    return jsonify(resources_data)

@admin_bp.route('/stats')
@login_required
@admin_required
def get_stats():
    """System statistics for admin dashboard"""
    total_users = User.query.count()
    total_events = Event.query.count()
    total_requests = Request.query.count()
    pending_requests = Request.query.filter_by(status='Pending').count()
    total_donations = Donation.query.count()
    
    # Resource utilization
    resources = Resource.query.all()
    resource_utilization = []
    for resource in resources:
        if resource.total_quantity > 0:
            utilization = ((resource.total_quantity - resource.available_quantity) / resource.total_quantity) * 100
        else:
            utilization = 0
        resource_utilization.append({
            'name': resource.name,
            'utilization': round(utilization, 2)
        })
    
    return jsonify({
        'total_users': total_users,
        'total_events': total_events,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'total_donations': total_donations,
        'resource_utilization': resource_utilization
    })