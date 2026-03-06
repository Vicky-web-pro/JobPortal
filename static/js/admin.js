/**
 * JobPortal - Admin JavaScript
 * Handles admin dashboard functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin panel loaded');
    
    // Initialize any admin-specific functionality
    initAdminFeatures();
});

function initAdminFeatures() {
    // Add any initialization code here
    // For example, auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 5000);
}

// Export functions for global use
window.Admin = {
    showMessage: function(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
        
        const container = document.querySelector('.admin-content') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(function() {
            alertDiv.style.transition = 'opacity 0.5s';
            alertDiv.style.opacity = '0';
            setTimeout(function() {
                alertDiv.remove();
            }, 500);
        }, 3000);
    },
    
    confirmDelete: function(itemName) {
        return confirm(`Are you sure you want to delete this ${itemName}?`);
    },
    
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }
};

