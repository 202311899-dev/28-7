document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const errorContainer = document.getElementById('error-container');

    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent page reload

        errorContainer.innerHTML = ''; // Clear previous messages

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Registration successful -> redirect to login page
                window.location.href = '/login';
            } else {
                // Display error message returned from server
                showError(data.error || 'Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Error during registration:', error);
            showError('Unable to connect to the server. Please check your network.');
        }
    });

    function showError(message) {
        errorContainer.innerHTML = `<div class="alert-error">${message}</div>`;
    }
});