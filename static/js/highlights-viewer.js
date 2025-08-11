class HighlightsViewer {
    constructor() {
        this.userId = this.getOrCreateUserId();
        this.highlights = this.loadHighlights();
        this.render();
    }

    getOrCreateUserId() {
        let userId = localStorage.getItem('retro-os-user-id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('retro-os-user-id', userId);
        }
        return userId;
    }

    loadHighlights() {
        const saved = localStorage.getItem(`ereader-highlights-${this.userId}`);
        return saved ? JSON.parse(saved) : [];
    }

    render() {
        const container = document.getElementById('highlights-list');
        if (!container) {
            console.error('HighlightsViewer: Container not found');
            return;
        }
        
        if (this.highlights.length === 0) {
            container.innerHTML = '<p>No highlights yet.</p>';
            return;
        }
        
        const sorted = this.highlights.sort((a, b) => a.globalIndex - b.globalIndex);
        container.innerHTML = sorted.map(h => 
            `<div class="highlight-item">
                <div class="highlight-meta">${h.chapter.name}</div>
                <div class="highlight-text">${h.text}</div>
            </div>`
        ).join('');
    }
}

function initHighlightsViewer() {
    document.querySelectorAll('.highlights-viewer:not([data-initialized])').forEach(container => {
        container.setAttribute('data-initialized', 'true');
        new HighlightsViewer();
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHighlightsViewer);
} else {
    initHighlightsViewer();
}

if (typeof htmx !== 'undefined') {
    htmx.onLoad(initHighlightsViewer);
}