document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorContainer = document.getElementById('error-container');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Stop default form submit (page refresh)

        // Clear previous error messages
        errorContainer.innerHTML = '';

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Successful login -> Redirect to todos dashboard
                window.location.href = '/todos';
            } else {
                // Show error returned by Flask API
                showError(data.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Error during login:', error);
            showError('Server connection failed. Please check your network.');
        }
    });

    function showError(message) {
        errorContainer.innerHTML = `<div class="alert-error">${message}</div>`;
    }
});