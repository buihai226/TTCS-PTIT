// JavaScript for admin pages

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    checkAuthentication();

    // Handle logout
    document.querySelector('.logout-link').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });

    // Initialize DataTable if element exists
    if(document.getElementById('recentDetectionsTable')) {
        $('#recentDetectionsTable').DataTable({
            responsive: true,
            pageLength: 5,
            lengthMenu: [5, 10, 25],
            language: {
                search: "Tìm kiếm:",
                lengthMenu: "Hiển thị _MENU_ dòng",
                info: "Hiển thị _START_ đến _END_ của _TOTAL_ dòng",
                infoEmpty: "Hiển thị 0 đến 0 của 0 dòng",
                infoFiltered: "(lọc từ _MAX_ dòng)",
                paginate: {
                    first: "Đầu",
                    last: "Cuối",
                    next: "Sau",
                    previous: "Trước"
                }
            }
        });
    }

    // Refresh data button
    const refreshBtn = document.getElementById('refreshBtn');
    if(refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadDashboardData();
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('fa-spin');
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        });
    }

    // Load dashboard data
    loadDashboardData();
});

// Check if user is authenticated and has admin role
function checkAuthentication() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    if (!token) {
        // Redirect to login page if no token found
        window.location.href = 'login.html?redirect=admin.html';
        return;
    }
    
    // Fetch user info
    fetch('http://localhost:8001/api/auth/me', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success || data.user.role !== 'admin') {
            // Redirect to home page if user is not admin
            alert('Bạn không có quyền truy cập trang này!');
            window.location.href = 'index.html';
            return;
        }
        
        // Update admin info on page
        updateAdminInfo(data.user);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Phiên đăng nhập của bạn đã hết hạn. Vui lòng đăng nhập lại.');
        window.location.href = 'login.html?redirect=admin.html';
    });
}

// Logout function
function logout() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    fetch('http://localhost:8001/api/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        // Clear token and user info
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        localStorage.removeItem('userInfo');
        
        // Redirect to login page
        window.location.href = 'login.html';
    })
    .catch(error => {
        console.error('Error:', error);
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        localStorage.removeItem('userInfo');
        window.location.href = 'login.html';
    });
}

// Update admin info on page
function updateAdminInfo(user) {
    if (document.getElementById('admin-name')) {
        document.getElementById('admin-name').textContent = user.fullname;
    }
    
    if (document.getElementById('admin-email')) {
        document.getElementById('admin-email').textContent = user.email;
    }
    
    // Get and format current time for last login
    const now = new Date();
    const options = { hour: '2-digit', minute: '2-digit' };
    const timeString = now.toLocaleTimeString([], options);
    
    if (document.getElementById('last-login')) {
        document.getElementById('last-login').textContent = `Hôm nay, ${timeString}`;
    }
    
    if (document.getElementById('last-update')) {
        document.getElementById('last-update').textContent = timeString;
    }
}

// Load dashboard data from API
function loadDashboardData() {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    
    if (!token) {
        return;
    }
    
    // Fetch dashboard statistics
    fetch('http://localhost:8001/api/admin/dashboard', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateDashboardStats(data.stats);
            updateRecentDetections(data.recentDetections);
        }
    })
    .catch(error => {
        console.error('Error loading dashboard data:', error);
    });
}

// Update dashboard statistics
function updateDashboardStats(stats) {
    // Use mock data for now
    if (!stats) {
        stats = {
            totalDetections: 1234,
            totalUsers: 48,
            todayDetections: 56,
            accuracyRate: 95.7
        };
    }
    
    if (document.getElementById('total-detections')) {
        document.getElementById('total-detections').textContent = stats.totalDetections.toLocaleString();
    }
    
    if (document.getElementById('total-users')) {
        document.getElementById('total-users').textContent = stats.totalUsers.toLocaleString();
    }
    
    if (document.getElementById('today-detections')) {
        document.getElementById('today-detections').textContent = stats.todayDetections.toLocaleString();
    }
    
    if (document.getElementById('accuracy-rate')) {
        document.getElementById('accuracy-rate').textContent = stats.accuracyRate.toFixed(1) + '%';
    }
}

// Update recent detections table
function updateRecentDetections(detections) {
    const tableBody = document.querySelector('#recentDetectionsTable tbody');
    if (!tableBody) return;
    
    // Use mock data for now
    if (!detections || !detections.length) {
        detections = [
            { id: 1, license_plate: '51F-123.45', confidence: 98.5, timestamp: '30/05/2025, 08:30:15', username: 'user1' },
            { id: 2, license_plate: '29A-456.78', confidence: 97.2, timestamp: '30/05/2025, 08:25:33', username: 'admin' },
            { id: 3, license_plate: '43B-789.01', confidence: 95.8, timestamp: '30/05/2025, 08:20:47', username: 'user2' },
            { id: 4, license_plate: '30H-234.56', confidence: 92.3, timestamp: '30/05/2025, 08:15:22', username: 'user1' },
            { id: 5, license_plate: '92C-567.89', confidence: 94.7, timestamp: '30/05/2025, 08:10:05', username: 'admin' }
        ];
    }
    
    // Clear existing table data
    tableBody.innerHTML = '';
    
    // Add new data
    detections.forEach(detection => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${detection.id}</td>
            <td><span class="license-plate-cell">${detection.license_plate}</span></td>
            <td>${detection.confidence.toFixed(1)}%</td>
            <td>${detection.timestamp}</td>
            <td>${detection.username}</td>
            <td class="actions-cell">
                <button class="btn btn-sm btn-info action-btn" title="Xem chi tiết">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-danger action-btn" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Refresh DataTable if it exists
    if ($.fn.DataTable.isDataTable('#recentDetectionsTable')) {
        $('#recentDetectionsTable').DataTable().destroy();
    }
    
    $('#recentDetectionsTable').DataTable({
        responsive: true,
        pageLength: 5,
        lengthMenu: [5, 10, 25],
        language: {
            search: "Tìm kiếm:",
            lengthMenu: "Hiển thị _MENU_ dòng",
            info: "Hiển thị _START_ đến _END_ của _TOTAL_ dòng",
            infoEmpty: "Hiển thị 0 đến 0 của 0 dòng",
            infoFiltered: "(lọc từ _MAX_ dòng)",
            paginate: {
                first: "Đầu",
                last: "Cuối",
                next: "Sau",
                previous: "Trước"
            }
        }
    });
}
