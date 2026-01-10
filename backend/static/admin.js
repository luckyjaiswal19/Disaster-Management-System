/**
 * Admin Dashboard JavaScript
 * Handles request processing and admin-specific functionality
 */

// Global variables
let currentRequestId = null;
let currentAction = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    loadSystemStats();
    initializeAdminEventListeners();
});

function initializeAdminEventListeners() {
    // Action form submission
    const actionForm = document.getElementById('actionForm');
    if (actionForm) {
        actionForm.addEventListener('submit', handleActionSubmit);
    }
}

function processRequest(requestId, action) {
    currentRequestId = requestId;
    currentAction = action;
    
    const modal = new bootstrap.Modal(document.getElementById('actionModal'));
    const title = document.getElementById('actionModalTitle');
    const submitBtn = document.getElementById('actionSubmit');
    const warningDiv = document.getElementById('actionWarning');
    
    // Update modal based on action
    if (action === 'approve') {
        title.textContent = 'Approve Request';
        submitBtn.className = 'btn btn-success';
        submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> Approve Request';
        
        // Check if we need to show insufficient quantity warning
        const requestElement = document.querySelector(`[onclick*="processRequest(${requestId}, 'approve')"]`);
        if (requestElement.disabled) {
            warningDiv.className = 'alert alert-warning';
            warningDiv.innerHTML = '<i class="bi bi-exclamation-triangle"></i> <strong>Warning:</strong> Requested quantity exceeds available resources. Consider partial fulfillment or waiting for more donations.';
            warningDiv.classList.remove('d-none');
        } else {
            warningDiv.classList.add('d-none');
        }
    } else {
        title.textContent = 'Reject Request';
        submitBtn.className = 'btn btn-danger';
        submitBtn.innerHTML = '<i class="bi bi-x-lg"></i> Reject Request';
        warningDiv.classList.add('d-none');
    }
    
    // Clear previous comment
    document.getElementById('actionComment').value = '';
    modal.show();
}

async function handleActionSubmit(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('actionSubmit');
    const originalText = submitBtn.innerHTML;
    const comment = document.getElementById('actionComment').value;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Processing...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`/admin/requests/${currentRequestId}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: currentAction,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`Request ${currentAction === 'approve' ? 'approved' : 'rejected'} successfully!`, 'success');
            
            // Close modals
            bootstrap.Modal.getInstance(document.getElementById('actionModal')).hide();
            
            // Reload the page to reflect changes
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showAlert('Error: ' + data.error, 'danger');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    } catch (error) {
        console.error('Action error:', error);
        showAlert('Action failed: ' + error.message, 'danger');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function viewRequestDetails(requestId) {
    try {
        const response = await fetch(`/user/requests/${requestId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayRequestDetails(data);
        } else {
            showAlert('Error loading request details: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Details error:', error);
        showAlert('Failed to load request details', 'danger');
    }
}

function displayRequestDetails(request) {
    const modalContent = document.getElementById('requestDetailsContent');
    
    let responseHtml = '';
    if (request.response) {
        responseHtml = `
            <div class="alert alert-${request.response.action === 'Approved' ? 'success' : 'danger'}">
                <h6>Admin Response</h6>
                <p><strong>Action:</strong> ${request.response.action}</p>
                <p><strong>By:</strong> ${request.response.admin_name}</p>
                <p><strong>Comment:</strong> ${request.response.comment || 'No comment provided'}</p>
                <p><strong>Responded:</strong> ${new Date(request.response.responded_at).toLocaleString()}</p>
            </div>
        `;
    }
    
    modalContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Requester:</strong> ${request.user_name}</p>
                <p><strong>Resource:</strong> ${request.resource_name}</p>
                <p><strong>Event:</strong> ${request.event_name}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Quantity:</strong> ${request.quantity}</p>
                <p><strong>Urgency:</strong> <span class="badge bg-${getUrgencyBadgeClass(request.urgency)}">${request.urgency}</span></p>
                <p><strong>Status:</strong> <span class="badge bg-${getStatusBadgeClass(request.status)}">${request.status}</span></p>
                <p><strong>Created:</strong> ${new Date(request.created_at).toLocaleString()}</p>
            </div>
        </div>
        ${responseHtml}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('requestDetailsModal'));
    modal.show();
}

async function loadSystemStats() {
    try {
        const response = await fetch('/admin/stats');
        const data = await response.json();
        
        if (response.ok) {
            displaySystemStats(data);
        }
    } catch (error) {
        console.error('Stats loading error:', error);
    }
}

function displaySystemStats(stats) {
    const container = document.getElementById('statsContainer');
    
    const utilizationHtml = stats.resource_utilization.map(resource => `
        <div class="mb-2">
            <div class="d-flex justify-content-between">
                <span>${resource.name}</span>
                <span>${resource.utilization}%</span>
            </div>
            <div class="progress" style="height: 8px;">
                <div class="progress-bar ${getUtilizationClass(resource.utilization)}" 
                     style="width: ${Math.min(resource.utilization, 100)}%">
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="row text-center mb-3">
            <div class="col-4">
                <h5>${stats.total_users}</h5>
                <small class="text-muted">Users</small>
            </div>
            <div class="col-4">
                <h5>${stats.total_events}</h5>
                <small class="text-muted">Events</small>
            </div>
            <div class="col-4">
                <h5>${stats.total_donations}</h5>
                <small class="text-muted">Donations</small>
            </div>
        </div>
        <hr>
        <h6>Resource Utilization</h6>
        ${utilizationHtml}
    `;
}

// Utility functions
function getUrgencyBadgeClass(urgency) {
    const classes = {
        'Critical': 'danger',
        'High': 'warning',
        'Medium': 'info',
        'Low': 'success'
    };
    return classes[urgency] || 'secondary';
}

function getStatusBadgeClass(status) {
    const classes = {
        'Pending': 'warning',
        'Approved': 'success',
        'Rejected': 'danger',
        'Fulfilled': 'info'
    };
    return classes[status] || 'secondary';
}

function getUtilizationClass(utilization) {
    if (utilization >= 80) return 'bg-danger';
    if (utilization >= 60) return 'bg-warning';
    if (utilization >= 40) return 'bg-info';
    return 'bg-success';
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Export for global access
window.adminUtils = {
    processRequest,
    viewRequestDetails,
    showAlert
};