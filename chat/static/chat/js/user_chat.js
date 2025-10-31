
// ====== Load existing messages ======
messageHistory.forEach(msg => {
    displayMessage(msg.sender, msg.content, msg.sender === username, msg.timestamp);
});

// ====== 1️⃣ Private Chat WebSocket ======
const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/user/' + recipientname + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    displayMessage(data.username, data.message, data.username === username);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// Send messages
const input = document.getElementById('chat-message-input');
const sendButton = document.getElementById('chat-message-submit');

input.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') sendButton.click();
});

sendButton.onclick = function() {
    const message = input.value.trim();
    if (!message) return;
    chatSocket.send(JSON.stringify({ 'message': message }));
    input.value = '';
    displayMessage(username, message, true);
};

// ====== UI Helpers ======
function displayMessage(user, text, isSender, time = new Date().toLocaleTimeString()) {
    const msg = document.createElement('div');
    msg.classList.add('message', isSender ? 'sent' : 'received');
    msg.innerHTML = `
        <div class="username">${user}</div>
        <div class="text">${text}</div>
        <div class="time">${time}</div>
    `;
    messagesContainer.appendChild(msg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function joinRoom(room) {
    window.location.href = '/chat/room/' + room + '/';
}

function startPrivateChat(recipient) {
    window.location.href = '/chat/user/' + recipient + '/';
}

// 🔔 Show a new message alert next to a username
function showNotification(sender) {
    const userItem = document.getElementById(`user-${sender}`);
    if (userItem) {
        userItem.style.fontWeight = "bold";
        userItem.style.color = "red";
        if (!userItem.querySelector('.new-msg')) {
            const badge = document.createElement('span');
            badge.classList.add('new-msg');
            badge.textContent = ' (new)';
            badge.style.color = 'orange';
            userItem.appendChild(badge);
        }
    }
}
