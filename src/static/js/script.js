// DOM Elements
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

// License plate result elements
const licensePlateText = document.getElementById('licensePlateText');
const confidenceText = document.getElementById('confidenceText');
const vehicleTypeText = document.getElementById('vehicleTypeText');
const timestampText = document.getElementById('timestampText');
const regionText = document.getElementById('regionText');

// Current upload type
let currentUploadType = 'image';

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Upload type selection
    imageBtn.addEventListener('click', () => setUploadType('image'));
    videoBtn.addEventListener('click', () => setUploadType('video'));
    
    // File upload handling
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop handling
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // Button actions
    recognizeBtn.addEventListener('click', processRecognition);
    demoBtn.addEventListener('click', showDemoResults);
    clearResultsBtn.addEventListener('click', clearResults);
    copyBtn.addEventListener('click', copyLicensePlate);
});

// Set upload type (image or video)
function setUploadType(type) {
    currentUploadType = type;
    
    if (type === 'image') {
        imageBtn.classList.add('active');
        imageBtn.classList.remove('btn-outline-primary');
        imageBtn.classList.add('btn-primary');
        
        videoBtn.classList.remove('active');
        videoBtn.classList.remove('btn-primary');
        videoBtn.classList.add('btn-outline-primary');
        
        fileInput.setAttribute('accept', 'image/*');
        uploadPrompt.querySelector('h4').textContent = 'Kéo và thả hình ảnh vào đây';
        uploadPrompt.querySelector('p.small').textContent = 'Hỗ trợ: JPG, PNG, JPEG';
    } else {
        videoBtn.classList.add('active');
        videoBtn.classList.remove('btn-outline-primary');
        videoBtn.classList.add('btn-primary');
        
        imageBtn.classList.remove('active');
        imageBtn.classList.remove('btn-primary');
        imageBtn.classList.add('btn-outline-primary');
        
        fileInput.setAttribute('accept', 'video/*');
        uploadPrompt.querySelector('h4').textContent = 'Kéo và thả video vào đây';
        uploadPrompt.querySelector('p.small').textContent = 'Hỗ trợ: MP4, MOV, AVI';
    }
    
    // Reset preview
    resetPreview();
}

// Handle file selection from input
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    displayFilePreview(file);
}

// Handle drag over event
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('bg-light');
}

// Handle drag leave event
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('bg-light');
}

// Handle drop event
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('bg-light');
    
    const file = e.dataTransfer.files[0];
    if (!file) return;
    
    // Check if file type matches current selection
    const fileType = file.type.split('/')[0];
    if ((currentUploadType === 'image' && fileType !== 'image') || 
        (currentUploadType === 'video' && fileType !== 'video')) {
        alert(`Vui lòng tải lên ${currentUploadType === 'image' ? 'hình ảnh' : 'video'}`);
        return;
    }
    
    displayFilePreview(file);
}

// Display file preview
function displayFilePreview(file) {
    const fileType = file.type.split('/')[0];
    
    // Create object URL
    const objectUrl = URL.createObjectURL(file);
    
    // Hide upload prompt, show preview
    uploadPrompt.classList.add('d-none');
    previewContainer.classList.remove('d-none');
    
    // Display appropriate preview
    if (fileType === 'image') {
        imagePreview.src = objectUrl;
        imagePreview.classList.remove('d-none');
        videoPreview.classList.add('d-none');
    } else if (fileType === 'video') {
        videoPreview.src = objectUrl;
        videoPreview.classList.remove('d-none');
        imagePreview.classList.add('d-none');
    }
    
    // Enable recognize button
    recognizeBtn.disabled = false;
}

// Reset preview
function resetPreview() {
    // Clear file input
    fileInput.value = '';
    
    // Show upload prompt, hide preview
    uploadPrompt.classList.remove('d-none');
    previewContainer.classList.add('d-none');
    
    // Clear previews
    imagePreview.src = '';
    videoPreview.src = '';
    
    // Disable recognize button
    recognizeBtn.disabled = true;
}

// Process recognition (simulated)
function processRecognition() {
    // Show loading state
    recognizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Đang xử lý...';
    recognizeBtn.disabled = true;
    
    // Simulate processing delay
    setTimeout(() => {
        // Generate random license plate for demo
        const results = {
            licensePlate: '51F-123.45',
            confidence: 98.7,
            vehicleType: 'Sedan',
            timestamp: new Date().toLocaleString('vi-VN'),
            region: 'TP. Hồ Chí Minh'
        };
        
        // Display results
        displayResults(results);
        
        // Reset button
        recognizeBtn.innerHTML = 'Nhận diện biển số xe';
        recognizeBtn.disabled = false;
    }, 2000);
}

// Display recognition results
function displayResults(results) {
    // Update result fields
    licensePlateText.textContent = results.licensePlate;
    confidenceText.textContent = results.confidence + '%';
    vehicleTypeText.textContent = results.vehicleType;
    timestampText.textContent = results.timestamp;
    regionText.textContent = results.region;
    
    // Show results section, hide no results section
    resultsSection.classList.remove('d-none');
    noResultsSection.classList.add('d-none');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show demo results
function showDemoResults() {
    const demoResults = {
        licensePlate: '51F-123.45',
        confidence: 98.7,
        vehicleType: 'Sedan',
        timestamp: new Date().toLocaleString('vi-VN'),
        region: 'TP. Hồ Chí Minh'
    };
    
    displayResults(demoResults);
}

// Clear results
function clearResults() {
    // Hide results section, show no results section
    resultsSection.classList.add('d-none');
    noResultsSection.classList.remove('d-none');
    
    // Reset preview
    resetPreview();
}

// Copy license plate to clipboard
function copyLicensePlate() {
    const licensePlate = licensePlateText.textContent;
    navigator.clipboard.writeText(licensePlate)
        .then(() => {
            // Change button text temporarily
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