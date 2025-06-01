// JavaScript for authentication pages (login.html and register.html)

document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;
            
            // Validate form
            if (!username || !password) {
                showError('Vui lòng nhập đầy đủ thông tin đăng nhập');
                return;
            }
            
            // Create form data object
            const formData = {
                username: username,
                password: password,
                rememberMe: rememberMe
            };
            
            // Send login request
            fetch('http://localhost:8001/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Store token in localStorage or sessionStorage based on remember me option
                    if (rememberMe) {
                        localStorage.setItem('authToken', data.token);
                    } else {
                        sessionStorage.setItem('authToken', data.token);
                    }
                    
                    // Store user info
                    localStorage.setItem('userInfo', JSON.stringify(data.user));
                    
                    // Redirect to dashboard or home page
                    window.location.href = 'index.html';
                } else {
                    showError(data.message || 'Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Có lỗi xảy ra khi kết nối với máy chủ. Vui lòng thử lại sau.');
            });
        });
    }

    // Register form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fullname = document.getElementById('fullname').value;
            const email = document.getElementById('email').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const role = document.getElementById('role').value;
            const terms = document.getElementById('terms').checked;
            
            // Validate form
            if (!fullname || !email || !username || !password || !confirmPassword || !role) {
                showError('Vui lòng nhập đầy đủ thông tin đăng ký');
                return;
            }
            
            if (!terms) {
                showError('Vui lòng đồng ý với điều khoản và điều kiện');
                return;
            }
            
            // Validate username (at least 5 characters, no special characters)
            if (username.length < 5 || /[^\w.]/.test(username)) {
                showError('Tên đăng nhập phải có ít nhất 5 ký tự và không chứa ký tự đặc biệt');
                return;
            }
            
            // Validate password (at least 8 characters, including uppercase, lowercase, and number)
            if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
                showError('Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số');
                return;
            }
            
            // Validate passwords match
            if (password !== confirmPassword) {
                showError('Mật khẩu xác nhận không khớp');
                return;
            }
            
            // Validate email format
            if (!/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(email)) {
                showError('Email không hợp lệ');
                return;
            }
            
            // Create form data object
            const formData = {
                fullname: fullname,
                email: email,
                username: username,
                password: password,
                role: role
            };
            
            // Send register request
            fetch('http://localhost:8001/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showSuccess('Đăng ký thành công! Đang chuyển hướng đến trang đăng nhập...');
                    
                    // Redirect to login page after 2 seconds
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                } else {
                    showError(data.message || 'Đăng ký thất bại. Vui lòng thử lại.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Có lỗi xảy ra khi kết nối với máy chủ. Vui lòng thử lại sau.');
            });
        });
    }

    // Function to show error messages
    function showError(message) {
        const errorAlert = document.getElementById('error-alert');
        const errorMessage = document.getElementById('error-message');
        
        if (errorAlert && errorMessage) {
            errorMessage.textContent = message;
            errorAlert.classList.remove('d-none');
            
            // Hide error after 5 seconds
            setTimeout(() => {
                errorAlert.classList.add('d-none');
            }, 5000);
        }
    }

    // Function to show success messages
    function showSuccess(message) {
        const successAlert = document.getElementById('success-alert');
        const successMessage = document.getElementById('success-message');
        
        if (successAlert && successMessage) {
            successMessage.textContent = message;
            successAlert.classList.remove('d-none');
        }
    }
});
