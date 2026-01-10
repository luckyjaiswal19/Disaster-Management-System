/**
 * User Dashboard JavaScript
 * Handles donation and request form submissions with fetch API
 */

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Donation form submission
    const donateForm = document.getElementById('donateForm');
    if (donateForm) {
        donateForm.addEventListener('submit', handleDonationSubmit);
    }

    // Request form submission
    const requestForm = document.getElementById('requestForm');
    if (requestForm) {
        requestForm.addEventListener('submit', handleRequestSubmit);
    }
}

async function handleDonationSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Processing...';
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(form);
        
        const response = await fetch('/user/donate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Donation submitted successfully!', 'success');
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('donateModal')).hide();
            form.reset();
            // Reload page to show updated donations
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Donation error:', error);
        showAlert('Donation failed: ' + error.message, 'danger');
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function handleRequestSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Submitting...';
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(form);
        
        const response = await fetch('/user/requests', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Request submitted successfully! It will be reviewed by an administrator.', 'success');
            // Close modal and reset form
            bootstrap.Modal.getInstance(document.getElementById('requestModal')).hide();
            form.reset();
            // Reload page to show updated requests
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Request error:', error);
        showAlert('Request failed: ' + error.message, 'danger');
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to top of content
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Utility function to format numbers
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Export functions for potential use in other scripts
window.dashboardUtils = {
    showAlert,
    formatNumber
};