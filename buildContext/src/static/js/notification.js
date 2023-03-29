

function showToast(type, message) {
    var toastContainer = document.getElementById('toast-container');
    var toast = document.createElement('div');
    toast.classList.add('toast');
    toast.classList.add('toast-' + type);
    toast.innerHTML = '<button type="button" class="close" data-dismiss="toast">&times;</button>' + message;
    toastContainer.appendChild(toast);

    var closeButton = toast.querySelector('.close');
    closeButton.addEventListener('click', function() {
        toast.remove();
    });

    setTimeout(function() {
        toast.remove();
        location.reload();
    }, 5000);
}

// Show toast notifications with messages from the Python side
function show_toast(message_toast,message_flag ) {
    var msg =  message_toast;
    var flag = message_flag;
    
    if (flag == "success") {
        showToast('success', msg);
    }

    else {
        showToast('error', msg);
    }
}
