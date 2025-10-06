// ============================================================================
// GDPR Compliance Dashboard - Main JavaScript
// ============================================================================

// ============================================================================
// THEME MANAGEMENT
// ============================================================================
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'dark';
htmlElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('i');
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================
function showToast(message, type = 'info', title = null) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const iconClass = icons[type] || icons.info;
    const toastTitle = title || type.charAt(0).toUpperCase() + type.slice(1);
    
    toast.innerHTML = `
        <i class="fas ${iconClass} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${toastTitle}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="btn-icon btn-sm" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ============================================================================
// LOADING OVERLAY
// ============================================================================
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    const progress = document.getElementById('progressFill');
    const percentage = document.getElementById('loadingPercentage');
    
    if (overlay) overlay.style.display = 'flex';
    if (text) text.textContent = message;
    if (progress) progress.style.width = '0%';
    if (percentage) percentage.textContent = '0%';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

function updateLoadingProgress(percent, message = null) {
    const progress = document.getElementById('progressFill');
    const percentage = document.getElementById('loadingPercentage');
    const text = document.getElementById('loadingText');
    
    if (progress) progress.style.width = `${percent}%`;
    if (percentage) percentage.textContent = `${percent}%`;
    if (message && text) text.textContent = message;
}

// Simulate progress for analysis
function simulateAnalysisProgress() {
    const stages = [
        { percent: 10, message: '🔍 Retrieving GDPR context...' },
        { percent: 25, message: '📚 Analyzing 2,693 GDPR articles...' },
        { percent: 40, message: '🧠 Stage 1: Detecting violations...' },
        { percent: 60, message: '💡 Stage 2: Generating remediation...' },
        { percent: 75, message: '� Calculating risk scores...' },
        { percent: 90, message: '⏳ Finalizing analysis...' }
    ];
    
    let currentStage = 0;
    const interval = setInterval(() => {
        if (currentStage >= stages.length) {
            clearInterval(interval);
            return;
        }
        
        const stage = stages[currentStage];
        updateLoadingProgress(stage.percent, stage.message);
        currentStage++;
    }, 8000); // Update every 8 seconds
    
    return interval;
}

// ============================================================================
// FORM VALIDATION
// ============================================================================
function validateScenario(scenario) {
    if (!scenario || scenario.trim().length === 0) {
        showToast('Please enter a scenario to analyze', 'error', 'Validation Error');
        return false;
    }
    
    if (scenario.trim().length < 50) {
        showToast('Scenario must be at least 50 characters long', 'error', 'Validation Error');
        return false;
    }
    
    if (scenario.trim().length > 5000) {
        showToast('Scenario must be less than 5000 characters', 'error', 'Validation Error');
        return false;
    }
    
    return true;
}

// ============================================================================
// API CALLS
// ============================================================================
async function analyzeScenario(scenario) {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ scenario: scenario })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        return data;
    } catch (error) {
        console.error('Analysis error:', error);
        throw error;
    }
}

async function exportAnalysis(analysisId, format) {
    try {
        const response = await fetch(`/api/export/${analysisId}/${format}`);
        
        if (format === 'json') {
            const data = await response.json();
            downloadJSON(data, `gdpr_analysis_${analysisId}.json`);
        } else if (format === 'markdown') {
            const text = await response.text();
            downloadText(text, `gdpr_analysis_${analysisId}.md`);
        } else if (format === 'pdf') {
            const htmlContent = await response.text();
            downloadText(htmlContent, `gdpr_analysis_${analysisId}.html`);
        }
        
        showToast(`Report exported as ${format.toUpperCase()}`, 'success', 'Export Successful');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export report', 'error', 'Export Failed');
    }
}

async function deleteAnalysis(analysisId) {
    if (!confirm('Are you sure you want to delete this analysis?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/delete/${analysisId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Analysis deleted successfully', 'success');
            // Reload page or remove element
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error('Delete failed');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Failed to delete analysis', 'error');
    }
}

// ============================================================================
// DOWNLOAD HELPERS
// ============================================================================
function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ============================================================================
// CHARACTER COUNTER
// ============================================================================
function setupCharacterCounter(textareaId, counterId, maxLength = 5000) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    
    if (!textarea || !counter) return;
    
    textarea.addEventListener('input', () => {
        const length = textarea.value.length;
        counter.textContent = `${length}/${maxLength} characters`;
        
        if (length > maxLength) {
            counter.style.color = 'var(--color-critical)';
        } else if (length > maxLength * 0.9) {
            counter.style.color = 'var(--color-high)';
        } else {
            counter.style.color = 'var(--text-secondary)';
        }
    });
}

// ============================================================================
// COPY TO CLIPBOARD
// ============================================================================
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMessage, 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// ============================================================================
// ANIMATION HELPERS
// ============================================================================
function fadeIn(element, duration = 300) {
    element.style.opacity = 0;
    element.style.display = 'block';
    
    let start = null;
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = (timestamp - start) / duration;
        
        element.style.opacity = Math.min(progress, 1);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 300) {
    let start = null;
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = (timestamp - start) / duration;
        
        element.style.opacity = 1 - Math.min(progress, 1);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(animate);
}

// ============================================================================
// SEARCH/FILTER HELPERS
// ============================================================================
function filterElements(searchTerm, elements, dataAttribute = 'search') {
    searchTerm = searchTerm.toLowerCase();
    
    elements.forEach(element => {
        const text = element.getAttribute(`data-${dataAttribute}`)?.toLowerCase() || '';
        if (text.includes(searchTerm)) {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    });
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const search = document.querySelector('input[type="search"]');
        if (search) search.focus();
    }
    
    // Ctrl/Cmd + N: New analysis
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        window.location.href = '/analyze';
    }
    
    // Escape: Close modals/overlays
    if (e.key === 'Escape') {
        hideLoading();
    }
});

// ============================================================================
// AUTO-SAVE TO LOCAL STORAGE
// ============================================================================
function setupAutoSave(textareaId, storageKey) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;
    
    // Load saved draft
    const saved = localStorage.getItem(storageKey);
    if (saved) {
        textarea.value = saved;
        showToast('Draft restored', 'info');
    }
    
    // Auto-save on input
    let saveTimeout;
    textarea.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            localStorage.setItem(storageKey, textarea.value);
            
            // Show save indicator
            const indicator = document.getElementById('saveIndicator');
            if (indicator) {
                indicator.textContent = '💾 Draft saved';
                indicator.style.opacity = 1;
                setTimeout(() => {
                    indicator.style.opacity = 0;
                }, 2000);
            }
        }, 1000); // Save 1 second after typing stops
    });
}

// ============================================================================
// INITIALIZE ON PAGE LOAD
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 GDPR Compliance Dashboard initialized');
    
    // Setup character counters
    setupCharacterCounter('scenarioText', 'charCount');
    
    // Setup auto-save
    setupAutoSave('scenarioText', 'gdpr_scenario_draft');
    
    // Add smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ============================================================================
// EXPORT FUNCTIONS FOR GLOBAL USE
// ============================================================================
window.GDPRDashboard = {
    showToast,
    showLoading,
    hideLoading,
    updateLoadingProgress,
    simulateAnalysisProgress,
    validateScenario,
    analyzeScenario,
    exportAnalysis,
    deleteAnalysis,
    copyToClipboard
};
