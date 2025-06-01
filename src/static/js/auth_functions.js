// Add these to your existing script.js

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status
    checkAuthStatus();
    
    // Setup logout functionality
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
});

// Function to check if user is authenticated
function checkAuthStatus() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const authButtons = document.getElementById('authButtons');
    const userDropdown = document.getElementById('userDropdown');
    const adminLink = document.getElementById('adminLink');
    
    if (token) {
        // User is logged in
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        
        if (userDropdown) {
            userDropdown.classList.remove('d-none');
            
            // Set username in the dropdown
            const usernameElement = document.getElementById('username');
            if (usernameElement && userInfo.fullname) {
                usernameElement.textContent = userInfo.fullname;
            }
            
            // Show/hide admin link based on role
            if (adminLink && userInfo.role !== 'admin') {
                adminLink.classList.add('d-none');
            }
        }
        
        if (authButtons) {
            authButtons.classList.add('d-none');
        }
        
        // Verify token is still valid
        verifyToken(token);
    } else {
        // User is not logged in
        if (authButtons) {
            authButtons.classList.remove('d-none');
        }
        
        if (userDropdown) {
            userDropdown.classList.add('d-none');
        }
    }
}

// Function to verify token validity
function verifyToken(token) {
    fetch('http://localhost:8001/api/auth/me', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Token invalid');
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            throw new Error('Token invalid');
        }
        
        // Update user info if needed
        localStorage.setItem('userInfo', JSON.stringify(data.user));
    })
    .catch(error => {
        console.error('Token validation error:', error);
        // Clear invalid token
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        localStorage.removeItem('userInfo');
        
        // Update UI
        checkAuthStatus();
    });
}

// Function to handle logout
function logout() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    if (token) {
        fetch('http://localhost:8001/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            // Clear token regardless of server response
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            localStorage.removeItem('userInfo');
            
            // Update UI
            checkAuthStatus();
            
            // Optional: Show logout success message
            alert('Đăng xuất thành công!');
        })
        .catch(error => {
            console.error('Logout error:', error);
            // Clear token anyway
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            localStorage.removeItem('userInfo');
            
            // Update UI
            checkAuthStatus();
        });
    }
}
