"""
Volunteer routes for task assignment and status updates.
Allows users to sign up as volunteers and fulfill approved requests.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Request, VolunteerAssignment, User
from datetime import datetime

volunteer_bp = Blueprint('volunteer', __name__)

@volunteer_bp.route('/dashboard')
@login_required
def dashboard():
    """Volunteer dashboard showing available and assigned tasks"""
    if not current_user.is_volunteer:
        return render_template('volunteer_signup.html')
        
    # Get available tasks (Approved requests not yet assigned)
    # This query excludes requests that already have an assignment
    assigned_request_ids = db.session.query(VolunteerAssignment.request_id).all()
    assigned_ids = [r[0] for r in assigned_request_ids]
    
    available_tasks = Request.query.filter(
        Request.status == 'Approved',
        ~Request.id.in_(assigned_ids if assigned_ids else [-1])
    ).all()
    
    # Get my assignments
    my_assignments = VolunteerAssignment.query.filter_by(user_id=current_user.id).order_by(VolunteerAssignment.assigned_at.desc()).all()
    
    return render_template('volunteer_dashboard.html', 
                         available_tasks=available_tasks,
                         my_assignments=my_assignments)

@volunteer_bp.route('/signup', methods=['POST'])
@login_required
def signup():
    """Register current user as a volunteer"""
    current_user.is_volunteer = True
    db.session.commit()
    flash('Welcome to the volunteer team!', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/tasks/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_task(request_id):
    """Volunteer accepts a task"""
    if not current_user.is_volunteer:
        return jsonify({'error': 'Must be a volunteer'}), 403
        
    request_obj = Request.query.get_or_404(request_id)
    
    if request_obj.status != 'Approved':
        return jsonify({'error': 'Task not available'}), 400
        
    # Check if already assigned
    existing = VolunteerAssignment.query.filter_by(request_id=request_id).first()
    if existing:
        return jsonify({'error': 'Task already assigned'}), 409
        
    assignment = VolunteerAssignment(
        user_id=current_user.id,
        request_id=request_id,
        status='In Progress'
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    flash('Task accepted successfully', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/tasks/<int:assignment_id>/complete', methods=['POST'])
@login_required
def complete_task(assignment_id):
    """Mark task as completed"""
    assignment = VolunteerAssignment.query.get_or_404(assignment_id)
    
    if assignment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    assignment.status = 'Completed'
    assignment.completed_at = datetime.utcnow()
    
    # Update request status as well
    assignment.request_obj.status = 'Fulfilled'
    
    db.session.commit()
    
    flash('Task completed! Thank you for your help.', 'success')
    return redirect(url_for('volunteer.dashboard'))
