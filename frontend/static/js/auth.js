async function handleLogin(event) {
    event.preventDefault();
    const errorElement = document.getElementById('loginError');
    errorElement.style.display = 'none';

    const userData = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value
    };

    try {
        const response = await fetch('/api/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            // Store the token
            localStorage.setItem('authToken', data.access_token);
            // Redirect to main page
            window.location.href = '/';
        } else {
            errorElement.textContent = data.detail || 'Login failed';
            errorElement.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorElement.textContent = 'An error occurred during login';
        errorElement.style.display = 'block';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const errorElement = document.getElementById('registerError');
    errorElement.style.display = 'none';

    const userData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password: document.getElementById('registerPassword').value
    };

    try {
        const response = await fetch('/api/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            alert('Registration successful! Please login.');
            toggleForms();
        } else {
            errorElement.textContent = data.detail || 'Registration failed';
            errorElement.style.display = 'block';
        }
    } catch (error) {
        console.error('Registration error:', error);
        errorElement.textContent = 'An error occurred during registration';
        errorElement.style.display = 'block';
    }
}