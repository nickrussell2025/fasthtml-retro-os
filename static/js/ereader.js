class EReader {
    constructor() {
        this.text = '';
        this.pages = [];
        this.currentPage = 0;
        this.load();
    }
    
    async load() {
        const response = await fetch('/api/book/frankenstein');
        const raw = await response.text();
        const start = raw.indexOf('*To Mrs. Saville, England.*');
        
        this.text = raw.substring(start > -1 ? start : 0)
            .replace(/\r\n/g, '\n')
            .replace(/([a-zA-Z,;:.])\n([a-zA-Z])/g, '$1 $2')  // Join mid-sentence breaks
            .replace(/\n\n+/g, '\n\n')                        // Normalize paragraphs  
            .trim();
        
        this.splitNextChunk();
        this.show();
        this.setup();
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
            const testText = currentPageText + (currentPageText ? ' ' : '') + words[wordIndex];
            container.innerHTML = this.formatText(testText);
            
            if (container.scrollHeight > container.clientHeight + 15 && currentPageText) {
                this.pages.push(currentPageText);
                currentPageText = words[wordIndex];
                pagesAdded++;
            } else {
                currentPageText = testText;
            }
            
            wordIndex++;
        }
        
        if (currentPageText && pagesAdded < 20) {
            this.pages.push(currentPageText);
        }
    }
    
    formatText(text) {
        return text.split('\n\n')
            .filter(p => p.trim())
            .map(p => `<p style="margin: 0 0 0.3em 0; text-align: justify; line-height: 1.4;">${p.trim()}</p>`)
            .join('');
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
        if (this.currentPage >= this.pages.length - 2) {
            this.splitNextChunk();
        }
        
        const container = document.querySelector('.ereader-page');
        const pageText = this.pages[this.currentPage] || '';
        container.innerHTML = this.formatText(pageText);
        
        const pageInfo = document.querySelector('.ereader-nav span');
        if (pageInfo) pageInfo.textContent = `Page ${this.currentPage + 1}`;
        
        const prevBtn = document.querySelector('.ereader-nav button:first-child');
        const nextBtn = document.querySelector('.ereader-nav button:last-child');
        
        if (prevBtn) prevBtn.disabled = this.currentPage === 0;
        if (nextBtn) nextBtn.disabled = false;
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
}

new EReader();