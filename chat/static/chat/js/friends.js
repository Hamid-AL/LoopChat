 // ====== Navigation Functions ======
 function joinRoom(room) {
    window.location.href = '/chat/room/' + room + '/';
}

function startPrivateChat(recipient) {
    window.location.href = '/chat/user/' + recipient + '/';
}

// ====== Modal Functions ======
function openCreateRoomModal() {
    document.getElementById('createRoomModal').style.display = 'flex';
}

function closeCreateRoomModal() {
    document.getElementById('createRoomModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('createRoomModal');
    if (event.target === modal) {
        closeCreateRoomModal();
    }
}

// ====== Form Handling ======
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.disabled = true;
                button.textContent = 'Processing...';
            }
        });
    });
});


