var truelight = truelight || {};

truelight.toaster = (function() {
    var alertTimeout;

    function getAlertContainer() {
        var alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alert-container';
            alertContainer.classList.add('position-fixed', 'top-0', 'end-0', 'p-3', 'w-100', 'd-flex', 'justify-content-center');
            alertContainer.style.zIndex = 9999;
            document.body.appendChild(alertContainer);
        }
        return alertContainer;
    }

    function createAlert(message, className) {
        var alertElement = document.createElement('div');
        alertElement.innerHTML = `
            <div class="${className} alert-dismissible fade show" role="alert" style="min-width: 300px;">
                <i class="fa fa-exclamation-circle me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `.trim();
        return alertElement.firstChild;
    }

    function showAlert(type, message) {
        var alertContainer = getAlertContainer();
        var alertClass = {
            'success': 'alert alert-success col-md-4',
            'fail': 'alert alert-danger col-md-4'
        };

        clearTimeout(alertTimeout);
        alertContainer.innerHTML = ''; // Clear existing alerts

        var alertElement = createAlert(message, alertClass[type]);
        alertContainer.appendChild(alertElement);

        // Automatically dismiss the alert after 5 seconds
        alertTimeout = setTimeout(function() {
            $(alertElement).alert('close');
        }, 5000);

        // Initialize the Bootstrap alert (for Bootstrap 5)
        var bsAlert = new bootstrap.Alert(alertElement);
    }

    return {
        success: function(message) {
            showAlert('success', message);
        },
        fail: function(message) {
            showAlert('fail', message);
        }
    };
})();

// Example usage:
// truelight.toaster.success('This is a success message!');
// truelight.toaster.fail('This is an error message!');
