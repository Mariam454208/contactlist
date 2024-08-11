document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (username && email && password) {
        alert('Account created successfully!');
    } else {
        alert('Please fill in all fields.');
    }
});
