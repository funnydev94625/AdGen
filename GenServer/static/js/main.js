// Main JavaScript for Video Generation Engine

// Global variables
let currentTaskId = null;
let statusPollingInterval = null;

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Video generation functions
function generateVideo(prompt) {
    if (!prompt.trim()) {
        showNotification('Please enter a prompt', 'warning');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    showProgressSection();
    
    // Make API request
    fetch('/generate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            currentTaskId = data.task_id;
            startStatusPolling(data.task_id);
            showNotification('Video generation started successfully!', 'success');
        } else {
            throw new Error(data.error || 'Failed to start video generation');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'danger');
        setLoadingState(false);
        hideProgressSection();
    });
}

function startStatusPolling(taskId) {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
    
    statusPollingInterval = setInterval(() => {
        pollTaskStatus(taskId);
    }, 2000);
}

function pollTaskStatus(taskId) {
    fetch(`/status/${taskId}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateProgress(data.progress, data.message);
            
            if (data.status === 'completed') {
                clearInterval(statusPollingInterval);
                setLoadingState(false);
                showSuccessSection(data.video_path);
                showNotification('Video generated successfully!', 'success');
            } else if (data.status === 'failed') {
                clearInterval(statusPollingInterval);
                setLoadingState(false);
                showErrorSection(data.error || 'Video generation failed');
                showNotification(`Generation failed: ${data.error}`, 'danger');
            }
        } else {
            throw new Error(data.error || 'Failed to get task status');
        }
    })
    .catch(error => {
        console.error('Status polling error:', error);
        clearInterval(statusPollingInterval);
        setLoadingState(false);
        showErrorSection(`Status check failed: ${error.message}`);
        showNotification(`Status check failed: ${error.message}`, 'danger');
    });
}

function updateProgress(progress, message) {
    const progressBar = document.getElementById('progressBar');
    const progressMessage = document.getElementById('progressMessage');
    
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    if (progressMessage) {
        progressMessage.textContent = message;
    }
}

function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    if (progressSection) progressSection.style.display = 'block';
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
}

function showSuccessSection(videoPath) {
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    if (progressSection) progressSection.style.display = 'none';
    if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.classList.add('success-pulse');
        
        // Set download link
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn && videoPath) {
            const filename = videoPath.split('/').pop();
            downloadBtn.href = `/download/${filename}/`;
        }
    }
    if (errorSection) errorSection.style.display = 'none';
}

function showErrorSection(errorMessage) {
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    if (progressSection) progressSection.style.display = 'none';
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) {
        errorSection.style.display = 'block';
        errorSection.classList.add('error-shake');
        
        const errorMessageEl = document.getElementById('errorMessage');
        if (errorMessageEl) {
            errorMessageEl.textContent = errorMessage;
        }
    }
}

function hideProgressSection() {
    const progressSection = document.getElementById('progressSection');
    if (progressSection) progressSection.style.display = 'none';
}

function setLoadingState(loading) {
    const generateBtn = document.getElementById('generateBtn');
    const promptField = document.getElementById('prompt');
    
    if (generateBtn) {
        generateBtn.disabled = loading;
        if (loading) {
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        } else {
            generateBtn.innerHTML = '<i class="fas fa-play me-2"></i>Generate Video';
        }
    }
    
    if (promptField) {
        promptField.disabled = loading;
    }
}

// Form handling
function setupFormHandlers() {
    const videoForm = document.getElementById('videoForm');
    if (videoForm) {
        videoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const promptField = document.getElementById('prompt');
            const prompt = promptField ? promptField.value.trim() : '';
            
            if (!prompt) {
                showNotification('Please enter a prompt', 'warning');
                return;
            }
            
            generateVideo(prompt);
        });
    }
}

// Example prompt handling
function useExample(prompt) {
    const promptField = document.getElementById('prompt');
    if (promptField) {
        promptField.value = prompt;
        promptField.focus();
        
        // Scroll to form
        promptField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        showNotification('Example prompt loaded!', 'info');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Text copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showNotification('Failed to copy text to clipboard', 'danger');
    });
}

// Utility functions
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-save functionality
function setupAutoSave() {
    const promptField = document.getElementById('prompt');
    if (promptField) {
        const debouncedSave = debounce(function() {
            localStorage.setItem('videoPrompt', promptField.value);
        }, 1000);
        
        promptField.addEventListener('input', debouncedSave);
        
        // Restore saved prompt
        const savedPrompt = localStorage.getItem('videoPrompt');
        if (savedPrompt && !promptField.value) {
            promptField.value = savedPrompt;
        }
    }
}

// URL parameter handling
function handleURLParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const prompt = urlParams.get('prompt');
    
    if (prompt) {
        const promptField = document.getElementById('prompt');
        if (promptField) {
            promptField.value = decodeURIComponent(prompt);
            showNotification('Prompt loaded from URL', 'info');
        }
    }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const videoForm = document.getElementById('videoForm');
            if (videoForm) {
                videoForm.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to clear form
        if (e.key === 'Escape') {
            const promptField = document.getElementById('prompt');
            if (promptField && document.activeElement === promptField) {
                promptField.value = '';
                localStorage.removeItem('videoPrompt');
            }
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
    setupAutoSave();
    handleURLParameters();
    setupKeyboardShortcuts();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in-up');
    }
    
    console.log('Video Generation Engine initialized');
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
});
