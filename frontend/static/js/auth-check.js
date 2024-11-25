// Check if we're on the auth page
const isAuthPage = window.location.pathname.includes('/auth');

// Authentication check function
async function checkAuth() {
    const token = localStorage.getItem('authToken');
    
    if (!token && !isAuthPage) {
        // Only redirect if we're not already on the auth page
        window.location.href = '/auth';
        return false;
    } else if (token && isAuthPage) {
        // If we have a token and we're on auth page, redirect to main page
        window.location.href = '/';
        return false;
    }
    return true;
}

async function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/auth';
}

function getAuthHeader() {
    const token = localStorage.getItem('authToken');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

async function getUserInfo() {
    try {
        const response = await fetch('/api/users/me', {
            headers: getAuthHeader()
        });
        
        if (!response.ok) {
            throw new Error('Authentication failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Auth check failed:', error);
        if (!isAuthPage) {
            window.location.href = '/auth';
        }
        return null;
    }
}

// Run auth check on page load
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
});