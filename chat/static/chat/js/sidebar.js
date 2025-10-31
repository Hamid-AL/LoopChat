function joinRoom(room) {
    window.location.href = '/chat/room/' + room + '/';
}

function startPrivateChat(recipient) {
    window.location.href = '/chat/user/' + recipient + '/';
}