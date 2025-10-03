/**
 * Azure Video Upload - Main Application JavaScript
 * Handles file uploads, drag-and-drop, progress tracking, and API integration
 */

// ===== Configuration =====
const CONFIG = {
    API_ENDPOINTS: {
        UPLOAD: '/api/upload',
        VIDEOS: '/api/videos',
        HEALTH: '/api/health'
    },
    MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
    ALLOWED_EXTENSIONS: ['mp4', 'mov', 'avi', 'mkv', 'webm'],
    NOTIFICATION_TIMEOUT: 5000 // 5 seconds
};

// ===== State Management =====
const state = {
    uploadingFiles: new Map(),
    uploadedVideos: []
};

// ===== DOM Elements =====
const elements = {
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    uploadBtn: document.getElementById('uploadBtn'),
    progressSection: document.getElementById('progressSection'),
    progressList: document.getElementById('progressList'),
    uploadCount: document.getElementById('uploadCount'),
    videosList: document.getElementById('videosList'),
    videoCount: document.getElementById('videoCount'),
    emptyState: document.getElementById('emptyState'),
    notificationContainer: document.getElementById('notificationContainer'),
    healthCheckBtn: document.getElementById('healthCheckBtn')
};

// ===== Utility Functions =====

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Get file extension from filename
 */
function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

/**
 * Validate file type
 */
function isValidFileType(filename) {
    const extension = getFileExtension(filename);
    return CONFIG.ALLOWED_EXTENSIONS.includes(extension);
}

/**
 * Validate file size
 */
function isValidFileSize(size) {
    return size <= CONFIG.MAX_FILE_SIZE;
}

/**
 * Get icon class for file type
 */
function getFileIcon(filename) {
    const ext = getFileExtension(filename);
    const icons = {
        'mp4': 'bi-file-earmark-play',
        'mov': 'bi-file-earmark-play-fill',
        'avi': 'bi-film',
        'mkv': 'bi-camera-video',
        'webm': 'bi-play-circle'
    };
    return icons[ext] || 'bi-file-earmark';
}

// ===== Notification System =====

/**
 * Show notification
 */
function showNotification(type, title, message) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.setAttribute('role', 'alert');
    
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-x-circle-fill',
        info: 'bi-info-circle-fill'
    };
    
    notification.innerHTML = `
        <i class="bi ${icons[type]} notification-icon" aria-hidden="true"></i>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <p class="notification-message">${message}</p>
        </div>
        <button class="notification-close" aria-label="Close notification">
            <i class="bi bi-x"></i>
        </button>
    `;
    
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => removeNotification(notification));
    
    elements.notificationContainer.appendChild(notification);
    
    // Auto-dismiss after timeout
    setTimeout(() => removeNotification(notification), CONFIG.NOTIFICATION_TIMEOUT);
}

/**
 * Remove notification
 */
function removeNotification(notification) {
    notification.classList.add('notification-exit');
    setTimeout(() => notification.remove(), 300);
}

// ===== Progress Tracking =====

/**
 * Create progress item
 */
function createProgressItem(file) {
    const progressItem = document.createElement('div');
    progressItem.className = 'progress-item';
    progressItem.id = `progress-${file.name}-${Date.now()}`;
    
    progressItem.innerHTML = `
        <div class="progress-item-header">
            <div class="progress-item-filename">
                <i class="bi ${getFileIcon(file.name)}" aria-hidden="true"></i>
                <span>${file.name}</span>
            </div>
            <span class="progress-item-percentage">0%</span>
        </div>
        <div class="progress">
            <div class="progress-bar bg-primary" role="progressbar" 
                 style="width: 0%" 
                 aria-valuenow="0" 
                 aria-valuemin="0" 
                 aria-valuemax="100"
                 aria-label="Upload progress for ${file.name}">
            </div>
        </div>
    `;
    
    return progressItem;
}

/**
 * Update progress item
 */
function updateProgress(progressItemId, percentage) {
    const progressItem = document.getElementById(progressItemId);
    if (!progressItem) return;
    
    const progressBar = progressItem.querySelector('.progress-bar');
    const percentageText = progressItem.querySelector('.progress-item-percentage');
    
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    percentageText.textContent = `${percentage}%`;
    
    if (percentage === 100) {
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-success');
    }
}

/**
 * Show/hide progress section
 */
function toggleProgressSection(show) {
    elements.progressSection.style.display = show ? 'block' : 'none';
}

/**
 * Update upload count
 */
function updateUploadCount() {
    const count = state.uploadingFiles.size;
    const total = elements.progressList.children.length;
    elements.uploadCount.textContent = `(${total - count} of ${total} files)`;
    
    if (count === 0 && total > 0) {
        setTimeout(() => {
            elements.progressList.innerHTML = '';
            toggleProgressSection(false);
        }, 2000);
    }
}

// ===== Video List Management =====

/**
 * Create video list item
 */
function createVideoItem(video) {
    const videoItem = document.createElement('div');
    videoItem.className = 'video-item';
    
    const uploadDate = video.uploaded_at ? new Date(video.uploaded_at).toLocaleString() : 'Unknown';
    
    videoItem.innerHTML = `
        <i class="bi ${getFileIcon(video.filename)} video-item-icon" aria-hidden="true"></i>
        <div class="video-item-info">
            <div class="video-item-name">${video.filename}</div>
            <div class="video-item-meta">
                <span><i class="bi bi-hdd" aria-hidden="true"></i> ${formatFileSize(video.size)}</span>
                <span><i class="bi bi-calendar3" aria-hidden="true"></i> ${uploadDate}</span>
            </div>
        </div>
        <div class="video-item-status">
            <span class="badge badge-success">
                <i class="bi bi-check-circle" aria-hidden="true"></i> Uploaded
            </span>
        </div>
    `;
    
    return videoItem;
}

/**
 * Update videos list
 */
function updateVideosList() {
    if (state.uploadedVideos.length === 0) {
        elements.emptyState.style.display = 'block';
        elements.videoCount.textContent = '0';
        return;
    }
    
    elements.emptyState.style.display = 'none';
    elements.videoCount.textContent = state.uploadedVideos.length;
    
    // Clear existing items except empty state
    const existingItems = elements.videosList.querySelectorAll('.video-item');
    existingItems.forEach(item => item.remove());
    
    // Add video items (newest first)
    const sortedVideos = [...state.uploadedVideos].reverse();
    sortedVideos.forEach(video => {
        const videoItem = createVideoItem(video);
        elements.videosList.insertBefore(videoItem, elements.emptyState);
    });
}

/**
 * Load videos from API
 */
async function loadVideos() {
    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.VIDEOS);
        const data = await response.json();
        
        if (data.success) {
            state.uploadedVideos = data.videos || [];
            updateVideosList();
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        showNotification('error', 'Error', 'Failed to load videos list');
    }
}

// ===== File Upload =====

/**
 * Upload single file
 */
async function uploadFile(file) {
    const progressItem = createProgressItem(file);
    const progressItemId = progressItem.id;
    elements.progressList.appendChild(progressItem);
    state.uploadingFiles.set(file.name, file);
    
    toggleProgressSection(true);
    updateUploadCount();
    
    const formData = new FormData();
    formData.append('files[]', file);
    
    try {
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentage = Math.round((e.loaded / e.total) * 100);
                updateProgress(progressItemId, percentage);
            }
        });
        
        // Handle completion
        xhr.addEventListener('load', () => {
            state.uploadingFiles.delete(file.name);
            updateUploadCount();
            
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success && response.files && response.files.length > 0) {
                    const uploadedFile = response.files[0];
                    state.uploadedVideos.push(uploadedFile);
                    updateVideosList();
                    showNotification('success', 'Upload Successful', `${file.name} uploaded successfully`);
                } else {
                    showNotification('error', 'Upload Failed', response.message || 'Unknown error occurred');
                }
            } else {
                showNotification('error', 'Upload Failed', `Server returned status ${xhr.status}`);
            }
            
            // Remove progress item after brief delay
            setTimeout(() => progressItem.remove(), 1500);
        });
        
        // Handle errors
        xhr.addEventListener('error', () => {
            state.uploadingFiles.delete(file.name);
            updateUploadCount();
            showNotification('error', 'Upload Error', `Failed to upload ${file.name}`);
            progressItem.remove();
        });
        
        xhr.open('POST', CONFIG.API_ENDPOINTS.UPLOAD);
        xhr.send(formData);
        
    } catch (error) {
        state.uploadingFiles.delete(file.name);
        updateUploadCount();
        showNotification('error', 'Upload Error', error.message);
        progressItem.remove();
    }
}

/**
 * Handle file selection
 */
function handleFiles(files) {
    const fileArray = Array.from(files);
    
    if (fileArray.length === 0) {
        showNotification('info', 'No Files', 'Please select at least one file');
        return;
    }
    
    // Validate and upload files
    fileArray.forEach(file => {
        // Validate file type
        if (!isValidFileType(file.name)) {
            showNotification('error', 'Invalid File Type', 
                `${file.name} is not a supported video format. Allowed: ${CONFIG.ALLOWED_EXTENSIONS.join(', ').toUpperCase()}`);
            return;
        }
        
        // Validate file size
        if (!isValidFileSize(file.size)) {
            showNotification('error', 'File Too Large', 
                `${file.name} exceeds the maximum file size of ${formatFileSize(CONFIG.MAX_FILE_SIZE)}`);
            return;
        }
        
        // Upload file
        uploadFile(file);
    });
    
    // Clear file input
    elements.fileInput.value = '';
}

// ===== Event Handlers =====

/**
 * Handle click on upload button
 */
elements.uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent event from bubbling to upload zone
    elements.fileInput.click();
});

/**
 * Handle click on upload zone
 */
elements.uploadZone.addEventListener('click', (e) => {
    // Only trigger if clicking the zone itself, not child elements like the button
    if (e.target === elements.uploadZone || (e.target.closest('.upload-zone') && !e.target.closest('.btn-upload'))) {
        elements.fileInput.click();
    }
});

/**
 * Handle file input change
 */
elements.fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

/**
 * Handle drag over
 */
elements.uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone.classList.add('drag-over');
});

/**
 * Handle drag leave
 */
elements.uploadZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone.classList.remove('drag-over');
});

/**
 * Handle drop
 */
elements.uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    handleFiles(files);
});

/**
 * Handle keyboard activation of upload zone
 */
elements.uploadZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        elements.fileInput.click();
    }
});

/**
 * Health check button
 */
elements.healthCheckBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.HEALTH);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            const azureStatus = data.azure_storage === 'connected' ? 'Connected ✓' : 'Not Configured ⚠️';
            showNotification('success', 'System Healthy', `Application is running. Azure Storage: ${azureStatus}`);
        } else {
            showNotification('error', 'System Error', 'Application is not responding correctly');
        }
    } catch (error) {
        showNotification('error', 'Health Check Failed', error.message);
    }
});

// ===== Initialization =====

/**
 * Initialize application
 */
function init() {
    console.log('🚀 Azure Video Upload Application initialized');
    
    // Load existing videos
    loadVideos();
    
    // Hide progress section initially
    toggleProgressSection(false);
    
    // Show welcome notification
    showNotification('info', 'Welcome', 'Upload your first video to get started');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
