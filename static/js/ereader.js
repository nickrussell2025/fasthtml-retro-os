class EReader {
    constructor() {        
        this.paragraphs = [];
        this.text = '';
        this.pages = [];
        this.userId = this.getOrCreateUserId();
        this.highlights = this.loadHighlights();
        this.load();
        this.setupBasicHighlighting();
        this.currentChapter = { name: 'Unknown', index: 0 };
    }

    getOrCreateUserId() {
        let userId = localStorage.getItem('retro-os-user-id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('retro-os-user-id', userId);
        }
        return userId;
    }

    savePage() {
        localStorage.setItem(`ereader-page-${this.userId}`, this.currentPage);
    }

    updateProgressBar() {
        if (!this.text || this.pages.length === 0) return;
        
        const currentPosition = this.getTextPosition(this.currentPage);
        const totalTextLength = this.text.length;
        
        const bookProgressPercent = (currentPosition / totalTextLength) * 100;
        const chapterProgressPercent = this.calculateChapterProgress(currentPosition);
        
        localStorage.setItem(`ereader-progress-percent-${this.userId}`, bookProgressPercent.toFixed(1));
        
        const bookProgressBar = document.getElementById('book-progress-fill');
        const chapterProgressBar = document.getElementById('chapter-progress-fill');
        
        if (bookProgressBar) {
            bookProgressBar.style.width = `${bookProgressPercent}%`;
        }
        if (chapterProgressBar) {
            chapterProgressBar.style.width = `${chapterProgressPercent}%`;
        }
    }

    loadPage() {
        return parseInt(localStorage.getItem(`ereader-page-${this.userId}`) || '0');
    }

    saveHighlights() {
        localStorage.setItem(`ereader-highlights-${this.userId}`, JSON.stringify(this.highlights));
    }

    loadHighlights() {
        const saved = localStorage.getItem(`ereader-highlights-${this.userId}`);
        return saved ? JSON.parse(saved) : [];
    }

    initializeChapterBoundaries() {
        const cacheKey = `chapter-boundaries-${this.userId}-frankenstein`;
        const cached = localStorage.getItem(cacheKey);
        
        if (cached) {
            this.chapterBoundaries = JSON.parse(cached);
            return;
        }
        
        this.chapterBoundaries = this.calculateChapterBoundaries();
        localStorage.setItem(cacheKey, JSON.stringify(this.chapterBoundaries));
    }

    calculateChapterBoundaries() {
        const boundaries = [];
        const chapterPatterns = [/Letter\s+(\d+)/gi, /Chapter\s+(\d+)/gi];
        
        let lastEnd = 0;
        let chapterIndex = 0;
        
        for (const pattern of chapterPatterns) {
            let match;
            pattern.lastIndex = 0;
            
            while ((match = pattern.exec(this.text)) !== null) {
                if (match.index > lastEnd) {
                    boundaries.push({
                        name: match[0],
                        index: chapterIndex++,
                        startPos: lastEnd,
                        endPos: match.index
                    });
                    lastEnd = match.index;
                }
            }
        }
        
        if (lastEnd < this.text.length) {
            boundaries.push({
                name: "Final Chapter",
                index: chapterIndex,
                startPos: lastEnd,
                endPos: this.text.length
            });
        }
        
        return boundaries;
    }

    findCurrentChapter(currentPosition) {
        if (!this.chapterBoundaries) return null;
        return this.chapterBoundaries.find(chapter => 
            currentPosition >= chapter.startPos && currentPosition < chapter.endPos
        );
    }

    calculateChapterProgress(currentPosition) {
        const chapter = this.findCurrentChapter(currentPosition);
        if (!chapter) return 0;
        
        const chapterLength = chapter.endPos - chapter.startPos;
        const positionInChapter = currentPosition - chapter.startPos;
        
        return Math.min(100, (positionInChapter / chapterLength) * 100);
    }
    
    async load() {
        const response = await fetch('/api/book/frankenstein');
        const raw = await response.text();
        
        this.processBookText(raw);
        this.initializeChapterBoundaries();
        this.splitNextChunk();
        
        const savedPage = this.loadPage();
        
        this.currentPage = savedPage;
        
        this.isLoaded = true;
        this.show();
        this.setup();
    }

    processBookText(raw) {
        const start = raw.indexOf('*To Mrs. Saville, England.*');
        
        this.text = raw.substring(start > -1 ? start : 0)
            .replace(/\r\n/g, '\n')
            .replace(/([a-zA-Z,;:.])\n([a-zA-Z])/g, '$1 $2')
            .replace(/\n\n+/g, '\n\n')
            .trim();
        
        // Create paragraphs with IDs for fragment matching
        this.paragraphs = this.text.split('\n\n').map((text, index) => ({
            id: `frank_p_${index.toString().padStart(3, '0')}`,
            text: text.trim()
        }));
    }
    
    splitNextChunk() {
        const container = document.querySelector('.ereader-page');
        const startPos = this.getTextPosition(this.pages.length);
        const remainingText = this.text.substring(startPos);
        const words = remainingText.split(' ');
        
        let currentPageText = '';
        let wordIndex = 0;
        let pagesAdded = 0;
        
        while (wordIndex < words.length && pagesAdded < 20) {
            const chunkSize = Math.min(20, words.length - wordIndex);
            const wordChunk = words.slice(wordIndex, wordIndex + chunkSize);
            const testText = currentPageText + (currentPageText ? ' ' : '') + wordChunk.join(' ');
            
            container.innerHTML = this.formatText(testText, true);            
            if (container.scrollHeight > container.clientHeight + 25 && currentPageText) {
                if (chunkSize === 1) {
                    this.pages.push(currentPageText);
                    currentPageText = words[wordIndex];
                    pagesAdded++;
                    wordIndex++;
                } else {
                    while (wordIndex < words.length) {
                        const singleWordTest = currentPageText + (currentPageText ? ' ' : '') + words[wordIndex];
                        console.log(`SINGLE WORD TEST: "${words[wordIndex]}", LENGTH: ${singleWordTest.length}`);
                        container.innerHTML = this.formatText(singleWordTest, true);                        
                        if (container.scrollHeight > container.clientHeight + 25) {
                            this.pages.push(currentPageText);
                            currentPageText = words[wordIndex];
                            pagesAdded++;
                            wordIndex++;
                            break;
                        } else {
                            currentPageText = singleWordTest;
                            wordIndex++;
                        }
                    }
                }
            } else {
                currentPageText = testText;
                wordIndex += chunkSize;
            }
        }
        
        if (currentPageText && pagesAdded < 20) {
            this.pages.push(currentPageText);
        }
    }

    formatText(text, testing = false) {
        return text.split('\n\n')
            .filter(p => p.trim())
            .map(p => {
                const correctParagraphId = this.findParagraphIdForFragment(p.trim());
                const isHighlighted = this.highlights.some(h => h.id === correctParagraphId);
                const bgStyle = isHighlighted ? 'background-color: rgba(255, 255, 0, 0.3);' : '';
                
                const formattedText = p.trim()
                    .replace(/\n/g, ' ')
                    .replace(/_(.*?)_/g, '<em>$1</em>');
                
                // Use left-align for testing, justify for display
                const textAlign = testing ? 'left' : 'justify';
                
                return `<p data-id="${correctParagraphId}" style="margin: 0 0 0.5em 0; text-align: ${textAlign}; line-height: 1.4; ${bgStyle}">${formattedText}</p>`;
            }).join('');
    }

    findParagraphIdForFragment(fragment) {
        for (const paragraph of this.paragraphs) {
            if (paragraph.text.includes(fragment.substring(0, 50))) {
                return paragraph.id;
            }
        }
        return 'unknown';
    }
    
    getTextPosition(pageIndex) {
        let position = 0;
        for (let i = 0; i < pageIndex; i++) {
            if (this.pages[i]) {
                position += this.pages[i].length + 1;
            }
        }
        return position;
    }
    
    show() {
        if (this.currentPage >= this.pages.length) {
            this.currentPage = 0;
        }
        if (this.currentPage < 0) {
            this.currentPage = 0;
        }
        
        if (this.currentPage >= this.pages.length - 2) {
            this.splitNextChunk();
        }
        
        const container = document.querySelector('.ereader-page');
        if (!container) {
            console.error('EReader: Container not found');
            return;
        }
        
        const pageText = this.pages[this.currentPage] || '';
        container.innerHTML = this.formatText(pageText, false);
        this.updateCurrentChapter();
        
        const pageInfo = document.querySelector('.ereader-nav span');
        if (pageInfo) pageInfo.textContent = `Page ${this.currentPage + 1}`;
        
        const prevBtn = document.querySelector('.ereader-nav button:first-child');
        const nextBtn = document.querySelector('.ereader-nav button:last-child');
        
        if (prevBtn) prevBtn.disabled = this.currentPage === 0;
        if (nextBtn) nextBtn.disabled = false;

        this.savePage();
        this.updateProgressBar();

    }
    
    setup() {
        const prevBtn = document.querySelector('.ereader-nav button:first-child');
        const nextBtn = document.querySelector('.ereader-nav button:last-child');
        
        if (nextBtn) nextBtn.onclick = () => {
            this.currentPage++;
            this.show();
        };
        
        if (prevBtn) prevBtn.onclick = () => {
            if (this.currentPage > 0) {
                this.currentPage--;
                this.show();
            }
        };
    }

    setupBasicHighlighting() {
        document.addEventListener('click', (e) => {
            const paragraph = e.target.closest('p[data-id]');
            if (!paragraph || !paragraph.closest('.ereader-page')) return;
            
            const paragraphId = paragraph.getAttribute('data-id');
            
            if (this.highlights.some(h => h.id === paragraphId)) {
                this.highlights = this.highlights.filter(h => h.id !== paragraphId);
            } else {
                const enrichedHighlight = this.createEnrichedHighlight(paragraphId);
                this.highlights.push(enrichedHighlight);
            }
            
            this.saveHighlights();
            this.refreshHighlights();
        });
    }

    createEnrichedHighlight(paragraphId) {
        const paragraph = this.paragraphs.find(p => p.id === paragraphId);
        if (!paragraph) return null;
        
        return {
            id: paragraphId,
            text: paragraph.text,
            timestamp: new Date().toISOString(),
            chapter: this.detectChapterForParagraph(paragraph),
            globalIndex: this.paragraphs.indexOf(paragraph),
            preview: paragraph.text.substring(0, 100) + '...'
        };
    }

    detectChapterForParagraph(paragraph) {
        return this.currentChapter;
    }

    parseChapterNumber(roman) {
        const romanNumerals = { I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6, VII: 7, VIII: 8, IX: 9, X: 10 };
        return romanNumerals[roman] || parseInt(roman) || 0;
    }

    updateCurrentChapter() {
        const pageText = this.pages[this.currentPage] || '';
        const detected = this.detectChapterInText(pageText);
        if (detected.name !== 'Unknown') {
            this.currentChapter = detected;
        }
    }

    detectChapterInText(text) {
        // Look for letter headers first
        if (text.includes('Letter 1') && text.includes('_To Mrs. Saville, England._')) return { name: 'Letter 1', index: 1 };
        if (text.includes('Letter 2') && text.includes('_To Mrs. Saville, England._')) return { name: 'Letter 2', index: 2 };
        if (text.includes('Letter 3') && text.includes('_To Mrs. Saville, England._')) return { name: 'Letter 3', index: 3 };
        if (text.includes('Letter 4') && text.includes('_To Mrs. Saville, England._')) return { name: 'Letter 4', index: 4 };
        
        // Look for chapter headers
        const chapterMatch = text.match(/Chapter\s+(\d+)/i);
        if (chapterMatch) {
            return { name: `Chapter ${chapterMatch[1]}`, index: parseInt(chapterMatch[1]) + 4 };
        }
        
        return { name: 'Unknown', index: 0 };
    }

    exportHighlights() {
        return {
            book: 'frankenstein',
            user: this.userId,
            timestamp: new Date().toISOString(),
            total_highlights: this.highlights.length,
            highlights: this.highlights.sort((a, b) => a.globalIndex - b.globalIndex)
        };
    }

    refreshHighlights() {
        const container = document.querySelector('.ereader-page');
        if (!container) return;
        
        const pageText = this.pages[this.currentPage] || '';
        container.innerHTML = this.formatText(pageText, false);
    }
    reconnectDOM() {
        // Reinitialize for new window
        this.setup();
        this.show();
        console.log('EReader reconnected to new window');
    }
}

// Auto-initialize when HTMX loads new content
function initEReaders() {
    const containers = document.querySelectorAll('.ereader-page');
    if (containers.length > 0) {
        // Create new instance for each new window, but only one per session
        if (window.ereaderInstance) {
            // Reconnect existing instance to new DOM
            window.ereaderInstance.reconnectDOM();
        } else {
            window.ereaderInstance = new EReader();
        }
        console.log('EReader instance ready');
    }
    
    // Add library initialization
    if (document.querySelector('.library-container')) {
        initLibrary();
    }
}

// Run on page load and when HTMX adds new content
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEReaders);
} else {
    initEReaders();
}

if (typeof htmx !== 'undefined') {
    htmx.onLoad(initEReaders);
}

// Library functions - add at end of static/js/ereader.js
function populateLibraryProgress() {
    const userId = localStorage.getItem('retro-os-user-id');
    if (!userId) return;
    
    const progressKey = `ereader-progress-percent-${userId}`;
    const progress = parseFloat(localStorage.getItem(progressKey) || '0');
    
    const progressLabel = document.getElementById('progress-frankenstein');
    const progressBar = document.getElementById('progress-bar-frankenstein');
    const actionBtn = document.getElementById('action-frankenstein');
    
    if (progressLabel) progressLabel.textContent = `${progress.toFixed(1)}% complete`;
    if (progressBar) progressBar.style.width = `${progress}%`;
    if (actionBtn && progress > 0) actionBtn.textContent = 'Continue Reading';
}

function initLibrary() {
    console.log('Library interface loaded');
    populateLibraryProgress();
}
