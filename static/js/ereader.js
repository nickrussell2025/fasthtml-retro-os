class EReader {
    constructor() {
        this.paragraphs = [];
        this.text = '';
        this.pages = [];
        this.userId = this.getOrCreateUserId();
        this.currentPage = this.loadPage();
        this.highlights = this.loadHighlights();
        this.load();
        this.setupBasicHighlighting();
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
    
    async load() {
        const response = await fetch('/api/book/frankenstein');
        const raw = await response.text();
        
        this.processBookText(raw);
        this.splitNextChunk();
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
            
            console.log(`WORD: "${words[wordIndex]}", CURRENT LENGTH: ${currentPageText.length}, CONTAINER: ${container.clientHeight}px`);
            container.innerHTML = this.formatText(testText, true);
            console.log(`AFTER FORMAT: scrollHeight=${container.scrollHeight}px, fits=${container.scrollHeight <= container.clientHeight + 25}`);
            
            if (container.scrollHeight > container.clientHeight + 25 && currentPageText) {
                console.log(`OVERFLOW: height=${container.scrollHeight}, limit=${container.clientHeight + 25}, currentText ends with: "${currentPageText.slice(-20)}", testing word: "${words[wordIndex]}"`);
                console.log(`Container actual: ${container.clientHeight}px, CSS height: ${container.style.height}, computed: ${getComputedStyle(container).height}`);

                if (chunkSize === 1) {
                    this.pages.push(currentPageText);
                    currentPageText = words[wordIndex];
                    pagesAdded++;
                    wordIndex++;
                } else {
                    while (wordIndex < words.length) {
                        const singleWordTest = currentPageText + (currentPageText ? ' ' : '') + words[wordIndex];
                        console.log(`SINGLE WORD TEST: "${words[wordIndex]}", LENGTH: ${singleWordTest.length}`);
                        console.log(`WORD: "${words[wordIndex]}" - Before: ${container.scrollHeight}px`);
                        container.innerHTML = this.formatText(singleWordTest, true);
                        console.log(`WORD: "${words[wordIndex]}" - After: ${container.scrollHeight}px`);
                        console.log(`HTML: ${container.innerHTML.slice(0, 100)}...`);
                        console.log(`SINGLE WORD RESULT: scrollHeight=${container.scrollHeight}px, fits=${container.scrollHeight <= container.clientHeight + 25}`);
                        
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
        container.innerHTML = this.formatText(pageText, false); // ← ADD false here for justified display
        
        const pageInfo = document.querySelector('.ereader-nav span');
        if (pageInfo) pageInfo.textContent = `Page ${this.currentPage + 1}`;
        
        const prevBtn = document.querySelector('.ereader-nav button:first-child');
        const nextBtn = document.querySelector('.ereader-nav button:last-child');
        
        if (prevBtn) prevBtn.disabled = this.currentPage === 0;
        if (nextBtn) nextBtn.disabled = false;

        this.savePage();
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
                console.log('Removed highlight:', paragraphId);
            } else {
                const enrichedHighlight = this.createEnrichedHighlight(paragraphId);
                this.highlights.push(enrichedHighlight);
                console.log('Added highlight:', enrichedHighlight);
            }
            
            this.saveHighlights();
            this.show();
            console.log('Total highlights:', this.highlights.length);
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
        const text = paragraph.text;
        
        if (text.includes('*To Mrs. Saville')) return { name: 'Letter 1', index: 1 };
        if (text.includes('August 5th')) return { name: 'Letter 2', index: 2 };
        if (text.includes('August 19th')) return { name: 'Letter 3', index: 3 };
        if (text.includes('August 26th')) return { name: 'Letter 4', index: 4 };
        if (text.match(/^CHAPTER\s+(\d+|[IVX]+)/i)) {
            const match = text.match(/^CHAPTER\s+([IVX]+|\d+)/i);
            return { name: `Chapter ${match[1]}`, index: this.parseChapterNumber(match[1]) + 4 };
        }
        
        return { name: 'Unknown', index: 0 };
    }

    parseChapterNumber(roman) {
        const romanNumerals = { I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6, VII: 7, VIII: 8, IX: 9, X: 10 };
        return romanNumerals[roman] || parseInt(roman) || 0;
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

}

// Auto-initialize when HTMX loads new content
function initEReaders() {
    document.querySelectorAll('.ereader-page:not([data-initialized])').forEach(container => {
        container.setAttribute('data-initialized', 'true');
        new EReader();
    });
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