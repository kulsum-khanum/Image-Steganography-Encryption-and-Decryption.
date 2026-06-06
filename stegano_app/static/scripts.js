// Toggle password visibility for login and register pages
function togglePassword(id) {
    const input = document.getElementById(id);
    const icon = document.getElementById('icon-' + id);
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
    } else {
        input.type = 'password';
        icon.textContent = '👁️';
    }
}

// Handle image message encoding (placeholder)
function encodeMessage() {
    const fileInput = document.getElementById('imageFile');
    const messageInput = document.getElementById('message');

    const file = fileInput?.files[0];
    const message = messageInput?.value;

    if (!file) {
        alert("Please upload an image.");
        return;
    }

    if (!message) {
        alert("Please enter a message to hide.");
        return;
    }

    // TODO: Replace with actual steganography logic
    alert('Message encoded into the image!');
}

// Handle image message decoding (placeholder)
function decodeMessage() {
    const fileInput = document.getElementById('imageFile');
    const file = fileInput?.files[0];

    if (!file) {
        alert("Please upload an image with a hidden message.");
        return;
    }

    // TODO: Replace with actual decoding logic
    const decodedMessage = "This is a sample decoded message!";
    const output = document.getElementById('decodedMessage');
    if (output) output.innerText = decodedMessage;

    alert('Message decoded successfully!');
}

// Placeholder login handler
function handleLogin() {
    const username = document.getElementById('username')?.value;
    const password = document.getElementById('password')?.value;

    if (!username || !password) {
        alert("Please enter both username and password.");
        return;
    }

    // TODO: Replace with real backend authentication
    alert(`Welcome back, ${username}!`);
}

// Placeholder register handler
function handleRegister() {
    const username = document.getElementById('username')?.value;
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;

    if (!username || !email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    // TODO: Replace with real backend registration
    alert(`Account created for ${username}!`);
}
