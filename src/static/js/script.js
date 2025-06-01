const imageBtn = document.getElementById('imageBtn');
const videoBtn = document.getElementById('videoBtn');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadPrompt = document.getElementById('uploadPrompt');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const videoPreview = document.getElementById('videoPreview');
const recognizeBtn = document.getElementById('recognizeBtn');
const resultsSection = document.getElementById('results');
const noResultsSection = document.getElementById('noResults');
const demoBtn = document.getElementById('demoBtn');
const clearResultsBtn = document.getElementById('clearResultsBtn');
const copyBtn = document.getElementById('copyBtn');

const licensePlateText = document.getElementById('licensePlateText');
const confidenceText = document.getElementById('confidenceText');
const timestampText = document.getElementById('timestampText');

let currentUploadType = 'image';

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    if (!dropZone || !fileInput) {
        console.error('dropZone or fileInput not found');
        return;
    }
    imageBtn.addEventListener('click', () => setUploadType('image'));
    videoBtn.addEventListener('click', () => setUploadType('video'));
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    recognizeBtn.addEventListener('click', processRecognition);
    demoBtn.addEventListener('click', showDemoResults);
    clearResultsBtn.addEventListener('click', clearResults);
    copyBtn.addEventListener('click', copyLicensePlate);
});

function setUploadType(type) {
    console.log('Setting upload type:', type);
    currentUploadType = type;
    
    if (type === 'image') {
        imageBtn.classList.add('active', 'btn-primary');
        imageBtn.classList.remove('btn-outline-primary');
        videoBtn.classList.remove('active', 'btn-primary');
        videoBtn.classList.add('btn-outline-primary');
        fileInput.setAttribute('accept', 'image/*');
        uploadPrompt.querySelector('h4').textContent = 'Kéo và thả hình ảnh vào đây';
        uploadPrompt.querySelector('p.small').textContent = 'Hỗ trợ: JPG, PNG, JPEG';
    } else {
        videoBtn.classList.add('active', 'btn-primary');
        videoBtn.classList.remove('btn-outline-primary');
        imageBtn.classList.remove('active', 'btn-primary');
        imageBtn.classList.add('btn-outline-primary');
        fileInput.setAttribute('accept', 'video/*');
        uploadPrompt.querySelector('h4').textContent = 'Kéo và thả video vào đây';
        uploadPrompt.querySelector('p.small').textContent = 'Hỗ trợ: MP4, MOV, AVI';
    }
    resetPreview();
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    displayFilePreview(file);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('bg-light');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('bg-light');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('bg-light');
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const fileType = file.type.split('/')[0];
    if ((currentUploadType === 'image' && fileType !== 'image') || 
        (currentUploadType === 'video' && fileType !== 'video')) {
        alert(`Vui lòng tải lên ${currentUploadType === 'image' ? 'hình ảnh' : 'video'}`);
        return;
    }
    displayFilePreview(file);
}

function displayFilePreview(file) {
    console.log('Displaying preview for file:', file.name);
    const fileType = file.type.split('/')[0];
    const objectUrl = URL.createObjectURL(file);
    uploadPrompt.classList.add('d-none');
    previewContainer.classList.remove('d-none');
    if (fileType === 'image') {
        imagePreview.src = objectUrl;
        imagePreview.classList.remove('d-none');
        videoPreview.classList.add('d-none');
    } else {
        videoPreview.src = objectUrl;
        videoPreview.classList.remove('d-none');
        imagePreview.classList.add('d-none');
    }
    recognizeBtn.disabled = false;
}

function resetPreview() {
    fileInput.value = '';
    uploadPrompt.classList.remove('d-none');
    previewContainer.classList.add('d-none');
    imagePreview.src = '';
    videoPreview.src = '';
    recognizeBtn.disabled = true;
}

async function processRecognition() {
    recognizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Đang xử lý...';
    recognizeBtn.disabled = true;

    const file = fileInput.files[0];
    if (!file) {
        alert('Vui lòng chọn một tệp!');
        recognizeBtn.innerHTML = '<i class="fas fa-search me-1"></i> Nhận diện biển số xe';
        recognizeBtn.disabled = false;
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        console.log('Gửi yêu cầu tới http://localhost:8001/process');
        const response = await fetch('http://localhost:8001/process', {
            method: 'POST',
            body: formData,
            headers: headers    
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Lỗi HTTP: ${response.status} - ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();
        console.log('Dữ liệu nhận được:', data);
        displayResults(data);

    } catch (error) {
        console.error('Lỗi:', error);
        alert(`Lỗi khi xử lý: ${error.message}. Kiểm tra backend có chạy trên cổng 8001 không.`);
        resultsSection.classList.add('d-none');
        noResultsSection.classList.remove('d-none');
    } finally {
        recognizeBtn.innerHTML = '<i class="fas fa-search me-1"></i> Nhận diện biển số xe';
        recognizeBtn.disabled = false;
    }
}

function displayResults(data) {
    console.log('Hiển thị kết quả:', data);
    resultsSection.classList.remove('d-none');
    noResultsSection.classList.add('d-none');

    // Xóa nội dung cũ
    licensePlateText.textContent = '';
    confidenceText.textContent = '';
    timestampText.textContent = '';
    const allDetections = document.getElementById('allDetections');
    if (allDetections) {
        allDetections.innerHTML = '';
    }

    // Nếu không có phát hiện
    if (!data.detections || data.detections.length === 0) {
        resultsSection.classList.add('d-none');
        noResultsSection.classList.remove('d-none');
        noResultsSection.querySelector('h5').textContent = 'Không phát hiện được biển số';
        noResultsSection.querySelector('p').textContent = data.message || 'Không có biển số nào được phát hiện';
        return;
    }

    // Hiển thị phát hiện đầu tiên
    const firstResult = data.detections[0];
    licensePlateText.textContent = firstResult.license_plate;
    confidenceText.textContent = firstResult.confidence.toFixed(2) + '%';
    timestampText.textContent = data.timestamp;

    // Hiển thị tất cả phát hiện
    if (allDetections) {
        let detectionList = '<h6>Tất cả phát hiện:</h6><ul class="list-unstyled">';
        data.detections.forEach(det => {
            detectionList += `
                <li class="result-item">
                    <div>
                        <strong>Biển số:</strong> ${det.license_plate}<br>
                        <strong>Độ tin cậy:</strong> ${det.confidence.toFixed(2)}%<br>
                        <strong>Thời gian:</strong> ${det.timestamp}
                    </div>
                </li>`;
        });
        detectionList += '</ul>';
        allDetections.innerHTML = detectionList;
    }

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showDemoResults() {
    const demoResults = {
        detections: [{
            license_plate: '51F-123.45',
            confidence: 98.7,
            timestamp: new Date().toLocaleString('vi-VN')
        }],
        message: 'Phát hiện 1 biển số xe',
        timestamp: new Date().toLocaleString('vi-VN')
    };
    displayResults(demoResults);
}

function clearResults() {
    resultsSection.classList.add('d-none');
    noResultsSection.classList.remove('d-none');
    resetPreview();
    const allDetections = document.getElementById('allDetections');
    if (allDetections) {
        allDetections.innerHTML = '';
    }
}

function copyLicensePlate() {
    const licensePlate = licensePlateText.textContent;
    navigator.clipboard.writeText(licensePlate)
        .then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Đã sao chép';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        })
        .catch(err => {
            console.error('Could not copy text: ', err);
            alert('Không thể sao chép văn bản');
        });
}