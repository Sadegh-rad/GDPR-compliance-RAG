// ==================== KNOWLEDGE BASE ENHANCED JAVASCRIPT ====================

let currentResults = [];
let currentQuery = '';
let searchHistory = [];

// ==================== VIEW SWITCHER ====================
function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.knowledge-view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected view
    document.getElementById(viewName + 'View').classList.add('active');
    document.getElementById(viewName + 'ViewBtn').classList.add('active');
    
    // Track view change
    trackEvent('view_change', { view: viewName });
}

// ==================== SEARCH FUNCTIONALITY ====================
function quickSearch(query) {
    document.getElementById('knowledgeSearchInput').value = query;
    searchKnowledge();
}

async function searchKnowledge() {
    const query = document.getElementById('knowledgeSearchInput').value.trim();
    const topK = parseInt(document.getElementById('topKInput').value) || 10;
    const advancedMode = document.getElementById('advancedMode')?.checked || false;
    
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    // Add to search history
    if (!searchHistory.includes(query)) {
        searchHistory.unshift(query);
        if (searchHistory.length > 10) searchHistory.pop();
    }
    
    currentQuery = query;
    
    // Show loading
    document.getElementById('knowledgeLoading').style.display = 'block';
    document.getElementById('knowledgeResults').style.display = 'none';
    
    // Track search
    trackEvent('knowledge_search', { query, top_k: topK, advanced: advancedMode });
    
    try {
        const response = await fetch('/api/knowledge/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                query, 
                top_k: topK,
                advanced: advancedMode
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        currentResults = data.results;
        
        displayResults(data);
        
        showToast(`Found ${data.results.length} results in ${data.search_time_ms}ms`, 'success');
        
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed. Please try again.', 'error');
        document.getElementById('knowledgeLoading').style.display = 'none';
    }
}

// ==================== DISPLAY RESULTS ====================
function displayResults(data) {
    const resultsDiv = document.getElementById('knowledgeResults');
    const statsDiv = document.getElementById('resultsStats');
    const listDiv = document.getElementById('resultsList');
    
    // Hide loading, show results
    document.getElementById('knowledgeLoading').style.display = 'none';
    resultsDiv.style.display = 'block';
    
    // Update stats
    const avgScore = data.results.length > 0 
        ? (data.results.reduce((sum, r) => sum + r.score, 0) / data.results.length * 100).toFixed(1)
        : 0;
        
    statsDiv.innerHTML = `
        <div style="display: flex; gap: var(--spacing-lg); flex-wrap: wrap; align-items: center;">
            <div>
                <i class="fas fa-search"></i> Found <strong style="color: var(--primary-color);">${data.results.length}</strong> results for 
                "<strong>${currentQuery}</strong>"
            </div>
            <div style="color: var(--success-color);">
                <i class="fas fa-clock"></i> ${data.search_time_ms}ms
            </div>
            <div style="color: var(--info-color);">
                <i class="fas fa-percentage"></i> Avg relevance: ${avgScore}%
            </div>
        </div>
    `;
    
    // Display results
    if (data.results.length === 0) {
        listDiv.innerHTML = `
            <div class="result-card" style="text-align: center; padding: var(--spacing-xl);">
                <div style="font-size: 4rem; opacity: 0.3; margin-bottom: var(--spacing-md);">
                    <i class="fas fa-search"></i>
                </div>
                <h3 style="margin-bottom: var(--spacing-sm);">No results found</h3>
                <p style="color: var(--text-secondary);">
                    Try different keywords, broader terms, or check for typos.
                </p>
                <div style="margin-top: var(--spacing-md);">
                    <button onclick="quickSearch('data subject rights')" class="btn btn-primary">
                        Try: Data Subject Rights
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    listDiv.innerHTML = data.results.map((result, index) => {
        const relevanceColor = result.score > 0.7 ? 'var(--success-color)' : 
                               result.score > 0.5 ? 'var(--warning-color)' : 
                               'var(--text-secondary)';
        
        return `
            <div class="result-card" data-index="${index}">
                <!-- Header -->
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: var(--spacing-sm); flex-wrap: wrap; gap: var(--spacing-xs);">
                    <div style="display: flex; gap: var(--spacing-xs); flex-wrap: wrap;">
                        <span class="badge" style="background: linear-gradient(135deg, var(--primary-color), #1976D2); color: white; font-weight: 600;">
                            #${index + 1}
                        </span>
                        ${result.metadata.source ? `
                            <span class="badge" style="background: var(--success-color); color: white;">
                                <i class="fas fa-file-alt"></i> ${result.metadata.source}
                            </span>
                        ` : ''}
                        ${result.metadata.document_type ? `
                            <span class="badge" style="background: var(--info-color); color: white;">
                                <i class="fas fa-bookmark"></i> ${result.metadata.document_type}
                            </span>
                        ` : ''}
                        ${result.metadata.article_number ? `
                            <span class="badge" style="background: var(--warning-color); color: white;">
                                <i class="fas fa-section"></i> Article ${result.metadata.article_number}
                            </span>
                        ` : ''}
                    </div>
                    <div style="display: flex; align-items: center; gap: var(--spacing-xs);">
                        <div style="text-align: right; margin-right: var(--spacing-xs);">
                            <div style="color: var(--text-secondary); font-size: 0.75rem;">Relevance</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: ${relevanceColor};">
                                ${(result.score * 100).toFixed(1)}%
                            </div>
                        </div>
                        <div class="relevance-indicator" style="width: 50px; height: 50px; border-radius: 50%; background: conic-gradient(${relevanceColor} ${result.score * 360}deg, var(--bg-primary) 0deg); display: flex; align-items: center; justify-content: center;">
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center;">
                                <i class="fas fa-check" style="color: ${relevanceColor};"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Content -->
                <div style="margin: var(--spacing-md) 0; padding: var(--spacing-md); background: rgba(33, 150, 243, 0.05); border-radius: 8px; border-left: 3px solid var(--primary-color);">
                    <p style="line-height: 1.8; color: var(--text-primary); margin: 0;">
                        ${highlightText(result.text, currentQuery)}
                    </p>
                </div>
                
                <!-- Metadata -->
                ${result.metadata.article_number || result.metadata.recital_number || result.metadata.chunk_index !== undefined ? `
                    <div style="border-top: 1px solid var(--border-color); padding-top: var(--spacing-sm); margin-top: var(--spacing-sm); display: flex; flex-wrap: wrap; gap: var(--spacing-md); color: var(--text-secondary); font-size: 0.875rem;">
                        ${result.metadata.article_number ? `
                            <span><i class="fas fa-section"></i> <strong>Article ${result.metadata.article_number}</strong></span>
                        ` : ''}
                        ${result.metadata.recital_number ? `
                            <span><i class="fas fa-quote-left"></i> <strong>Recital ${result.metadata.recital_number}</strong></span>
                        ` : ''}
                        ${result.metadata.chunk_index !== undefined ? `
                            <span><i class="fas fa-file-alt"></i> Chunk ${result.metadata.chunk_index}</span>
                        ` : ''}
                        <span style="margin-left: auto;">
                            <button onclick="copyToClipboard(${index})" class="btn btn-sm" style="padding: 4px 12px;">
                                <i class="fas fa-copy"></i> Copy
                            </button>
                            <button onclick="shareResult(${index})" class="btn btn-sm" style="padding: 4px 12px;">
                                <i class="fas fa-share"></i> Share
                            </button>
                        </span>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Add animation
    setTimeout(() => {
        document.querySelectorAll('.result-card').forEach((card, i) => {
            setTimeout(() => {
                card.style.animation = 'fadeIn 0.5s ease forwards';
            }, i * 50);
        });
    }, 100);
}

// ==================== TEXT HIGHLIGHTING ====================
function highlightText(text, query) {
    if (!query) return text;
    
    const words = query.toLowerCase().split(' ').filter(w => w.length > 2);
    let highlighted = text;
    
    words.forEach(word => {
        const regex = new RegExp(`(${escapeRegex(word)})`, 'gi');
        highlighted = highlighted.replace(regex, '<mark style="background: linear-gradient(135deg, var(--warning-color), #FFA726); color: var(--bg-primary); padding: 2px 6px; border-radius: 4px; font-weight: 600;">$1</mark>');
    });
    
    return highlighted;
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ==================== SORTING ====================
function sortResults() {
    const sortBy = document.getElementById('sortBy').value;
    
    if (sortBy === 'score') {
        currentResults.sort((a, b) => b.score - a.score);
    } else if (sortBy === 'article') {
        currentResults.sort((a, b) => {
            const aNum = parseInt(a.metadata.article_number) || 999;
            const bNum = parseInt(b.metadata.article_number) || 999;
            return aNum - bNum;
        });
    }
    
    displayResults({ results: currentResults, search_time_ms: 0 });
}

// ==================== EXPORT FUNCTIONALITY ====================
function exportResults(format) {
    if (currentResults.length === 0) {
        showToast('No results to export', 'warning');
        return;
    }
    
    let content, filename, mimeType;
    
    if (format === 'markdown') {
        content = generateMarkdown(currentResults, currentQuery);
        filename = `gdpr_search_${new Date().toISOString().split('T')[0]}.md`;
        mimeType = 'text/markdown';
    } else if (format === 'json') {
        content = JSON.stringify({
            query: currentQuery,
            timestamp: new Date().toISOString(),
            results: currentResults
        }, null, 2);
        filename = `gdpr_search_${new Date().toISOString().split('T')[0]}.json`;
        mimeType = 'application/json';
    } else if (format === 'pdf') {
        // For PDF, we'll create HTML and let browser print to PDF
        printResultsAsPDF();
        return;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast(`Results exported as ${format.toUpperCase()}`, 'success');
    trackEvent('export_results', { format, count: currentResults.length });
}

function generateMarkdown(results, query) {
    let md = `# GDPR Knowledge Base Search Results\n\n`;
    md += `**Query:** ${query}\n`;
    md += `**Date:** ${new Date().toLocaleString()}\n`;
    md += `**Results:** ${results.length}\n\n`;
    md += `---\n\n`;
    
    results.forEach((result, index) => {
        md += `## ${index + 1}. Relevance: ${(result.score * 100).toFixed(1)}%\n\n`;
        
        if (result.metadata.source) {
            md += `**Source:** ${result.metadata.source}\n`;
        }
        if (result.metadata.document_type) {
            md += `**Type:** ${result.metadata.document_type}\n`;
        }
        if (result.metadata.article_number) {
            md += `**Article:** ${result.metadata.article_number}\n`;
        }
        if (result.metadata.recital_number) {
            md += `**Recital:** ${result.metadata.recital_number}\n`;
        }
        
        md += `\n### Content\n\n${result.text}\n\n`;
        md += `---\n\n`;
    });
    
    md += `\n_Generated by GDPR Compliance Dashboard_\n`;
    return md;
}

function printResultsAsPDF() {
    const printWindow = window.open('', '_blank');
    const html = generatePrintHTML(currentResults, currentQuery);
    printWindow.document.write(html);
    printWindow.document.close();
    setTimeout(() => {
        printWindow.print();
    }, 500);
}

function generatePrintHTML(results, query) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>GDPR Search Results - ${query}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2196F3; }
        .result { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .metadata { color: #666; font-size: 14px; }
        .score { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <h1>GDPR Knowledge Base Search Results</h1>
    <p><strong>Query:</strong> ${query}</p>
    <p><strong>Date:</strong> ${new Date().toLocaleString()}</p>
    <p><strong>Results:</strong> ${results.length}</p>
    <hr>
    ${results.map((r, i) => `
        <div class="result">
            <h3>#${i+1} - <span class="score">${(r.score * 100).toFixed(1)}% Relevance</span></h3>
            <div class="metadata">
                ${r.metadata.source ? `Source: ${r.metadata.source} | ` : ''}
                ${r.metadata.article_number ? `Article ${r.metadata.article_number}` : ''}
            </div>
            <p>${r.text}</p>
        </div>
    `).join('')}
</body>
</html>
    `;
}

// ==================== UTILITY FUNCTIONS ====================
function copyToClipboard(index) {
    const result = currentResults[index];
    const text = `${result.text}\n\nSource: ${result.metadata.source || 'GDPR'}\n${result.metadata.article_number ? 'Article ' + result.metadata.article_number : ''}`;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    });
}

function shareResult(index) {
    const result = currentResults[index];
    const shareData = {
        title: 'GDPR Knowledge - Search Result',
        text: result.text.substring(0, 200) + '...',
        url: window.location.href
    };
    
    if (navigator.share) {
        navigator.share(shareData);
    } else {
        copyToClipboard(index);
        showToast('Link copied! (Share API not supported)', 'info');
    }
}

// ==================== ARTICLE BROWSER ====================
function toggleChapter(chapterId) {
    const content = document.getElementById(chapterId);
    const icon = document.getElementById('icon-' + chapterId);
    
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.classList.add('rotated');
    } else {
        content.style.display = 'none';
        icon.classList.remove('rotated');
    }
}

function filterArticles(query) {
    const articles = document.querySelectorAll('.article-item');
    const searchLower = query.toLowerCase();
    
    articles.forEach(article => {
        const text = article.textContent.toLowerCase();
        article.style.display = text.includes(searchLower) ? 'flex' : 'none';
    });
}

function loadArticle(articleNumber) {
    // Search for the specific article
    quickSearch(`Article ${articleNumber}`);
    switchView('search');
}

// ==================== ANALYTICS ====================
function trackEvent(eventName, data) {
    console.log('Event:', eventName, data);
    // Add analytics tracking here (Google Analytics, Plausible, etc.)
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('knowledgeSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchKnowledge();
            }
        });
        
        // Focus on search with Ctrl+K or Cmd+K
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
});
