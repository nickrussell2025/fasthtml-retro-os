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
            
            container.innerHTML = this.formatText(testText);
            
            if (container.scrollHeight > container.clientHeight + 15 && currentPageText) {
                if (chunkSize === 1) {
                    this.pages.push(currentPageText);
                    currentPageText = words[wordIndex];
                    pagesAdded++;
                    wordIndex++;
                } else {
                    while (wordIndex < words.length) {
                        const singleWordTest = currentPageText + (currentPageText ? ' ' : '') + words[wordIndex];
                        container.innerHTML = this.formatText(singleWordTest);
                        
                        if (container.scrollHeight > container.clientHeight + 15) {
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

    formatText(text) {
        return text.split('\n\n')
            .filter(p => p.trim())
            .map(p => {
                const correctParagraphId = this.findParagraphIdForFragment(p.trim());
                const isHighlighted = this.highlights.includes(correctParagraphId);
                const bgStyle = isHighlighted ? 'background-color: rgba(255, 255, 0, 0.1);' : '';
                
                // Convert _text_ to italic formatting
                const formattedText = p.trim().replace(/_(.*?)_/g, '<em>$1</em>');
                
                return `<p data-id="${correctParagraphId}" style="margin: 0 0 0.3em 0; text-align: justify; line-height: 1.4; ${bgStyle}">${formattedText}</p><br>`;
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
        container.innerHTML = this.formatText(pageText);
        
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
            
            if (this.highlights.includes(paragraphId)) {
                this.highlights = this.highlights.filter(id => id !== paragraphId);
                console.log('Removed highlight:', paragraphId);
            } else {
                this.highlights.push(paragraphId);
                console.log('Added highlight:', paragraphId);
            }
            
            this.saveHighlights();
            this.show();
            console.log('Total highlights:', this.highlights.length);
        });
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