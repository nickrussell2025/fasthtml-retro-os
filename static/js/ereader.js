// ============================================
// STATE MANAGEMENT - Handles all localStorage and state
// ============================================
class ReaderState {
    constructor(userId) {
        this.userId = userId;
        this.currentPage = 0;
        this.savedPosition = 0;
        this.highlights = [];
        this.currentChapter = { name: 'Unknown', index: 0 };
        this.saveTimer = null;
        this.load();
    }
    
    load() {
        try {
            const highlights = localStorage.getItem(`ereader-highlights-${this.userId}`);
            if (highlights) {
                this.highlights = JSON.parse(highlights);
            }
            
            const savedPage = localStorage.getItem(`ereader-page-${this.userId}`);
            const savedPosition = localStorage.getItem(`ereader-position-${this.userId}`);
            
            if (savedPage) this.currentPage = parseInt(savedPage);
            if (savedPosition) this.savedPosition = parseInt(savedPosition);
            
            console.log('📖 Loaded state:', { 
                page: this.currentPage, 
                position: this.savedPosition,
                highlights: this.highlights.length 
            });
        } catch (e) {
            console.error('Failed to load state:', e);
        }
    }

    save(textPosition) {
        if (this.saveTimer) {
            clearTimeout(this.saveTimer);
        }
        
        this.saveTimer = setTimeout(() => {
            this._performSave(textPosition);
            this.saveTimer = null;
        }, 500);
    }
    
    saveNow(textPosition) {
        if (this.saveTimer) {
            clearTimeout(this.saveTimer);
            this.saveTimer = null;
        }
        this._performSave(textPosition);
    }
   
    _performSave(textPosition) {
        try {
            this.savedPosition = textPosition;
            
            localStorage.setItem(`ereader-page-${this.userId}`, this.currentPage);
            localStorage.setItem(`ereader-position-${this.userId}`, textPosition);
            localStorage.setItem(`ereader-highlights-${this.userId}`, JSON.stringify(this.highlights));
            localStorage.setItem('frankenstein-highlights', JSON.stringify(this.highlights));
            
            console.log('💾 Saved state:', { 
                page: this.currentPage, 
                position: textPosition,
                highlights: this.highlights.length 
            });
        } catch (e) {
            console.error('Failed to save:', e);
        }
    }
   
    updateProgress(position, totalLength) {
        if (!totalLength) return;
        
        const percent = (position / totalLength) * 100;
        localStorage.setItem(`ereader-progress-percent-${this.userId}`, percent.toFixed(1));
        
        const bookBar = document.getElementById('book-progress-fill');
        if (bookBar) bookBar.style.width = `${percent}%`;
        
        // Chapter progress (ADD THIS)
        const chapterPercent = this.calculateChapterProgress(position);
        const chapterBar = document.getElementById('chapter-progress-fill');
        if (chapterBar) {
            chapterBar.style.width = `${chapterPercent}%`;
        }

        console.log('📊 Progress:', percent.toFixed(1) + '%');
    }

    calculateChapterProgress(position) {
        // Access chapters from the loader through the parent EReader instance
        const chapters = window.ereaderInstance?.loader?.chapters;
        if (!chapters || !chapters.length) return 0;
        
        const chapter = chapters.find(c => position >= c.pos && position < c.endPos);
        if (!chapter) return 0;
        
        const chapterLength = chapter.endPos - chapter.pos;
        const positionInChapter = position - chapter.pos;
        return Math.min(100, Math.max(0, (positionInChapter / chapterLength) * 100));
    }
   
    toggleHighlight(paragraphId, paragraphText) {
        const index = this.highlights.findIndex(h => h.id === paragraphId);
        
        if (index >= 0) {
            this.highlights.splice(index, 1);
            console.log('🖍️ Removed highlight:', paragraphId);
        } else {
            this.highlights.push({
                id: paragraphId,
                text: paragraphText,
                timestamp: new Date().toISOString(),
                chapter: this.currentChapter
            });
            console.log('🖍️ Added highlight:', paragraphId);
        }
   }
}

// ============================================
// BOOK LOADER - Handles text processing and pagination
// ============================================
class BookLoader {
    constructor() {
        this.text = '';
        this.pages = [];
        this.paragraphs = [];
        this.chapters = [];
        this.isLoaded = false;
    }
    
    async loadBook() {
        try {
            console.log('📚 Loading book...');
            const response = await fetch('/api/book/frankenstein');
            if (!response.ok) throw new Error('Failed to load book');
            
            const raw = await response.text();
            this.processText(raw);
            this.findChapters();
            this.isLoaded = true;
            
            console.log('📚 Book loaded:', {
                length: this.text.length,
                paragraphs: this.paragraphs.length,
                chapters: this.chapters.length
            });
        } catch (e) {
            console.error('Failed to load book:', e);
            throw e;
        }
    }
    
    processText(raw) {
        const start = raw.indexOf('*To Mrs. Saville, England.*');
        
        // Single chain of replacements
        this.text = raw.substring(start > -1 ? start : 0)
            .replace(/<[^>]*>/g, '')
            .replace(/&(mdash|#8212);/g, '—')
            .replace(/&(nbsp|#160);/g, ' ')
            .replace(/&(quot|ldquo|rdquo|#8220|#8221);/g, '"')
            .replace(/&(lsquo|rsquo|#8216|#8217);/g, "'")
            .replace(/&(amp|#38);/g, '&')
            .replace(/&(hellip|#8230);/g, '...')
            .replace(/\r?\n/g, '\n')
            .replace(/([a-zA-Z,;:.])\n([a-zA-Z])/g, '$1 $2')
            .replace(/\n{2,}/g, '\n\n')
            .trim();
        
        this.paragraphs = this.text.split('\n\n').map((text, i) => ({
            id: `p_${i.toString().padStart(4, '0')}`,
            text: text.trim()
        }));
    }
    
    findChapters() {
        // Check cache
        const cached = localStorage.getItem('book-chapters-cache');
        if (cached) {
            this.chapters = JSON.parse(cached);
            return;
        }
        
        // Find all chapter/letter markers
        const markers = [];
        [/Letter \d+/g, /Chapter \d+/g].forEach(pattern => {
            let match;
            while ((match = pattern.exec(this.text)) !== null) {
                markers.push({ name: match[0], pos: match.index });
            }
        });
        
        // Sort and create boundaries
        markers.sort((a, b) => a.pos - b.pos);
        this.chapters = markers.map((m, i) => ({
            ...m,
            endPos: markers[i + 1]?.pos || this.text.length
        }));
        
        localStorage.setItem('book-chapters-cache', JSON.stringify(this.chapters));
    }
    
    generatePages(startPos = 0, count = 20) {
        const container = document.querySelector('.ereader-page');
        if (!container) return 0;
        
        // If starting fresh, clear pages
        if (startPos === 0) {
            this.pages = [];
        }
        
        const remainingText = this.text.substring(startPos);
        const words = remainingText.split(' ');
        let wordIndex = 0;
        let pagesAdded = 0;
        
        while (wordIndex < words.length && pagesAdded < count) {
            let currentPageText = '';
            
            // Try adding words in chunks first for efficiency
            while (wordIndex < words.length) {
                // Grab a chunk of words (start with 20)
                const chunkSize = Math.min(20, words.length - wordIndex);
                const wordChunk = words.slice(wordIndex, wordIndex + chunkSize);
                const testText = currentPageText + (currentPageText ? ' ' : '') + wordChunk.join(' ');
                
                container.innerHTML = this.formatText(testText, true);
                
                // If it fits, add the chunk
                if (container.scrollHeight <= container.clientHeight + 5) {
                    currentPageText = testText;
                    wordIndex += chunkSize;
                } else {
                    // Chunk doesn't fit, add word by word
                    if (chunkSize === 1) {
                        // Even a single word doesn't fit, save current page
                        if (currentPageText) {
                            this.pages.push(currentPageText);
                            pagesAdded++;
                            currentPageText = words[wordIndex];
                            wordIndex++;
                        } else {
                            // Single word is too big for empty page (shouldn't happen)
                            currentPageText = words[wordIndex];
                            wordIndex++;
                        }
                        break; // Start new page
                    } else {
                        // Try adding word by word from the chunk
                        for (let i = 0; i < chunkSize; i++) {
                            const singleTest = currentPageText + (currentPageText ? ' ' : '') + words[wordIndex];
                            container.innerHTML = this.formatText(singleTest, true);
                            
                            if (container.scrollHeight > container.clientHeight + 5) {
                                // This word makes it overflow, save page
                                if (currentPageText) {
                                    this.pages.push(currentPageText);
                                    pagesAdded++;
                                    currentPageText = '';
                                }
                                break; // Start new page
                            } else {
                                currentPageText = singleTest;
                                wordIndex++;
                            }
                        }
                        break; // After word-by-word, start fresh
                    }
                }
                
                // If we've added enough pages, stop
                if (pagesAdded >= count) break;
            }
            
            // Don't forget remaining text on last page
            if (currentPageText && pagesAdded < count && wordIndex >= words.length) {
                this.pages.push(currentPageText);
                pagesAdded++;
            }
        }
        
        console.log('📄 Generated', pagesAdded, 'pages. Total:', this.pages.length);
        return pagesAdded;
    }
    
    formatText(text, testing = false) {
        return text.split('\n\n')
            .filter(p => p.trim())
            .map(p => {
                const para = this.findParagraph(p.trim());
                const highlighted = window.ereaderInstance?.state?.highlights.some(h => h.id === para?.id);
                
                return `<p data-id="${para?.id || 'unknown'}" style="
                    margin: 0 0 0.5em 0;
                    text-align: ${testing ? 'left' : 'justify'};
                    line-height: 1.4;
                    ${highlighted ? 'background: rgba(255,255,0,0.3);' : ''}
                ">${p.trim().replace(/\n/g, ' ').replace(/_(.*?)_/g, '<em>$1</em>')}</p>`;
            }).join('');
    }
    
    findParagraph(text) {
        const preview = text.substring(0, 50);
        return this.paragraphs.find(p => p.text.includes(preview));
    }
    
    getTextPosition(pageIndex) {
        let pos = 0;
        for (let i = 0; i < pageIndex && i < this.pages.length; i++) {
            pos += this.pages[i].length + 1;
        }
        return pos;
    }
    
    findPageForPosition(position) {
        for (let i = 0; i < this.pages.length; i++) {
            const start = this.getTextPosition(i);
            const end = this.getTextPosition(i + 1);
            if (position >= start && position < end) {
                return i;
            }
        }
        return 0;
    }
    
    getCurrentChapter(position) {
        const chapter = this.chapters.find(c => position >= c.pos && position < c.endPos);
        return chapter ? { name: chapter.name, index: this.chapters.indexOf(chapter) } : null;
    }
}

// ============================================
// MAIN EREADER CLASS - Orchestrates everything
// ============================================
class EReader {
    constructor() {
        console.log('🚀 Initializing EReader...');
        this.userId = this.getOrCreateUserId();
        this.state = new ReaderState(this.userId);
        this.loader = new BookLoader();
        this.initialize();
    }
    
    getOrCreateUserId() {
        let userId = localStorage.getItem('retro-os-user-id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('retro-os-user-id', userId);
            console.log('👤 Created user:', userId);
        } else {
            console.log('👤 Existing user:', userId);
        }
        return userId;
    }
    
    async initialize() {
        try {
            await this.loader.loadBook();
            
            // Generate pages from beginning for consistency
            if (this.state.savedPosition > 0) {
                // Generate enough pages to reach saved position
                while (this.loader.getTextPosition(this.loader.pages.length) < this.state.savedPosition + 2000) {
                    const generated = this.loader.generatePages(
                        this.loader.getTextPosition(this.loader.pages.length)
                    );
                    if (generated === 0) break;
                }
                this.state.currentPage = this.loader.findPageForPosition(this.state.savedPosition);
                console.log('📍 Restored to page', this.state.currentPage);
            } else {
                this.loader.generatePages(0);
                this.state.currentPage = 0;
            }
            
            this.render();
            this.setupEventHandlers();
            console.log('✅ EReader ready');
        } catch (e) {
            console.error('❌ Initialization failed:', e);
            this.showError('Failed to load book. Please refresh.');
        }
    }
    
    render() {
        const container = document.querySelector('.ereader-page');
        if (!container) return;
        
        // Ensure we have enough pages ahead
        if (this.state.currentPage >= this.loader.pages.length - 2) {
            this.loader.generatePages(
                this.loader.getTextPosition(this.loader.pages.length)
            );
        }
        
        // Batch all DOM updates
        requestAnimationFrame(() => {
            // Render current page
            const pageText = this.loader.pages[this.state.currentPage] || '';
            container.innerHTML = this.loader.formatText(pageText);
            
            // Update all UI elements at once
            const pageInfo = document.querySelector('.ereader-nav span');
            const [prevBtn, nextBtn] = document.querySelectorAll('.ereader-nav button');
            
            if (pageInfo) pageInfo.textContent = `Page ${this.state.currentPage + 1}`;
            if (prevBtn) prevBtn.disabled = this.state.currentPage === 0;
            if (nextBtn) nextBtn.disabled = false;
        });
        
        // Save state (debounced)
        const position = this.loader.getTextPosition(this.state.currentPage);
        this.state.save(position);
        this.state.updateProgress(position, this.loader.text.length);
        
        // Update chapter
        const chapter = this.loader.getCurrentChapter(position);
        if (chapter) {
            this.state.currentChapter = chapter;
        }
    }
    
    updateUI() {
        const pageInfo = document.querySelector('.ereader-nav span');
        const [prevBtn, nextBtn] = document.querySelectorAll('.ereader-nav button');
        
        if (pageInfo) pageInfo.textContent = `Page ${this.state.currentPage + 1}`;
        if (prevBtn) prevBtn.disabled = this.state.currentPage === 0;
        if (nextBtn) nextBtn.disabled = false;
    }
    
    setupEventHandlers() {
        const [prevBtn, nextBtn] = document.querySelectorAll('.ereader-nav button');
        
        if (nextBtn) nextBtn.onclick = () => {
            this.state.currentPage++;
            this.render();
        };
        
        if (prevBtn) prevBtn.onclick = () => {
            if (this.state.currentPage > 0) {
                this.state.currentPage--;
                this.render();
            }
        };
        
        // Highlighting
        document.addEventListener('click', (e) => {
            const p = e.target.closest('p[data-id]');
            if (!p || !p.closest('.ereader-page')) return;
            
            const id = p.getAttribute('data-id');

            const para = this.loader.paragraphs.find(p => p.id === id);
            
            if (para) {
                this.state.toggleHighlight(id, para.text);
                this.state.saveNow(this.loader.getTextPosition(this.state.currentPage));
                this.render();
            }
        });
    }
    
    showError(message) {
        const container = document.querySelector('.ereader-page');
        if (container) {
            container.innerHTML = `<p style="color: red; text-align: center;">${message}</p>`;
        }
    }
    
    reconnect() {
        // For HTMX navigation - reconnect to new DOM
        console.log('🔄 Reconnecting to DOM');
        this.setupEventHandlers();
        this.render();
    }
}

// ============================================
// INITIALIZATION
// ============================================
window.ereaderInstance = null;

function initEReader() {
    console.log('🎬 Init check...');
    const container = document.querySelector('.ereader-page');
    
    if (container) {
        console.log('📚 EReader container found');
        if (window.ereaderInstance) {
            window.ereaderInstance.reconnect();
        } else {
            window.ereaderInstance = new EReader();
        }
    }
    
    // Library view
    if (document.querySelector('.library-container')) {
        initLibrary();
    }
}

function initLibrary() {
    const userId = localStorage.getItem('retro-os-user-id');
    if (!userId) return;
    
    const progress = parseFloat(localStorage.getItem(`ereader-progress-percent-${userId}`) || '0');
    console.log('📊 Library progress:', progress.toFixed(1) + '%');
    
    const progressLabel = document.getElementById('progress-frankenstein');
    const progressBar = document.getElementById('progress-bar-frankenstein');
    const actionBtn = document.getElementById('action-frankenstein');
    
    if (progressLabel) progressLabel.textContent = `${progress.toFixed(1)}% complete`;
    if (progressBar) progressBar.style.width = `${progress}%`;
    if (actionBtn && progress > 0) actionBtn.textContent = 'Continue Reading';
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEReader);
} else {
    initEReader();
}

// HTMX integration
if (typeof htmx !== 'undefined') {
    htmx.onLoad(initEReader);
}

// Debug helper
window.debugEReader = () => window.ereaderInstance ? {
    state: {
        page: window.ereaderInstance.state.currentPage,
        position: window.ereaderInstance.state.savedPosition,
        highlights: window.ereaderInstance.state.highlights.length
    },
    loader: {
        pages: window.ereaderInstance.loader.pages.length,
        chapters: window.ereaderInstance.loader.chapters.length
    }
} : 'No reader instance';