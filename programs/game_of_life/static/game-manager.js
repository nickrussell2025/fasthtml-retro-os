// Game of Life Manager - Extracted from inline script
class GameOfLifeManager {
    constructor() {
        this.intervals = new Map()
        this.setupHTMXListeners()
        this.initializeExistingGames()
        console.log('Game of Life Manager ready')
    }
    
    setupHTMXListeners() {
        // Clean up before HTMX swaps
        document.addEventListener('htmx:beforeSwap', (e) => {
            if (e.target.id === 'game-container') {
                console.log('Stopping game before HTMX swap')
                this.stopAutoRun(e.target)
            }
        })
        
        // Reinitialize after HTMX swaps
        document.addEventListener('htmx:afterSwap', (e) => {
            if (e.target.id === 'game-container') {
                console.log('Checking for auto-run after HTMX swap')
                setTimeout(() => this.checkAutoRun(e.target), 100)
            }
        })
    }
    
    initializeExistingGames() {
        // Find any existing games on page load
        document.querySelectorAll('#game-container').forEach(container => {
            this.checkAutoRun(container)
        })
    }
    
    checkAutoRun(gameContainer) {
        const statusElement = gameContainer.querySelector('#game-status')
        if (!statusElement) return
        
        const isAutoRunning = statusElement.textContent.includes('AUTO-RUNNING')
        console.log('Game auto-run status:', isAutoRunning)
        
        if (isAutoRunning) {
            this.startAutoRun(gameContainer)
        }
    }
    
    startAutoRun(gameContainer) {
        const gameId = this.getGameId(gameContainer)
        
        // Stop any existing interval
        this.stopAutoRun(gameContainer)
        
        // Extract game state from server-rendered DOM
        const gridElement = gameContainer.querySelector('#game-grid')
        if (!gridElement) {
            console.error('No game grid found')
            return
        }
        
        // Get initial state from the DOM (same as your working inline script)
        let grid = this.extractGridFromDOM(gridElement)
        let generation = this.extractGeneration(gameContainer)
        const height = grid.length
        const width = grid[0]?.length || 0
        
        console.log(`Starting Game of Life: ${width}x${height}, generation ${generation}`)
        
        // Start interval with same logic as your working inline script
        const interval = setInterval(() => {
            console.log('Auto-run step:', generation)
            
            // Conway's rules (same as inline script)
            const newGrid = []
            for (let y = 0; y < height; y++) {
                newGrid[y] = []
                for (let x = 0; x < width; x++) {
                    let neighbors = 0
                    for (let dy = -1; dy <= 1; dy++) {
                        for (let dx = -1; dx <= 1; dx++) {
                            if (dx === 0 && dy === 0) continue
                            const ny = y + dy, nx = x + dx
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width && grid[ny][nx]) {
                                neighbors++
                            }
                        }
                    }
                    newGrid[y][x] = grid[y][x] ? (neighbors === 2 || neighbors === 3) : (neighbors === 3)
                }
            }
            
            grid = newGrid
            generation++
            
            // Update status
            const statusEl = gameContainer.querySelector('#game-status')
            if (statusEl) {
                const liveCount = grid.flat().filter(c => c).length
                statusEl.textContent = `Generation: ${generation} • Live cells: ${liveCount} • AUTO-RUNNING`
            }
            
            // Update grid (same as inline script)
            const gridEl = gameContainer.querySelector('#game-grid')
            if (gridEl) {
                let html = ''
                for (let y = 0; y < height; y++) {
                    html += '<div style="display: flex;">'
                    for (let x = 0; x < width; x++) {
                        const bg = grid[y][x] ? 'var(--primary-color)' : 'transparent'
                        html += `<div onclick="htmx.ajax('POST', '/gameoflife/toggle/${x}/${y}', {target: '#game-grid', swap: 'innerHTML'})" style="width: 15px; height: 15px; border: 1px solid var(--primary-dim); cursor: pointer; background: ${bg};"></div>`
                    }
                    html += '</div>'
                }
                gridEl.innerHTML = html
            }
        }, 500)
        
        this.intervals.set(gameId, interval)
        console.log('Auto-run started for:', gameId)
    }
    
    stopAutoRun(gameContainer) {
        const gameId = this.getGameId(gameContainer)
        const interval = this.intervals.get(gameId)
        
        if (interval) {
            clearInterval(interval)
            this.intervals.delete(gameId)
            console.log('Auto-run stopped for:', gameId)
        }
    }
    
    extractGridFromDOM(gridElement) {
        // Extract current grid state from DOM (not from Python data)
        const rows = Array.from(gridElement.children)
        return rows.map(row => {
            const cells = Array.from(row.children)
            return cells.map(cell => {
                const bg = cell.style.background
                return bg.includes('var(--primary-color)') || 
                       (bg !== 'transparent' && bg !== '' && bg !== 'rgba(0, 0, 0, 0)')
            })
        })
    }
    
    extractGeneration(gameContainer) {
        const statusText = gameContainer.querySelector('#game-status')?.textContent || ''
        const match = statusText.match(/Generation: (\d+)/)
        return match ? parseInt(match[1]) : 0
    }
    
    getGameId(gameContainer) {
        const window = gameContainer.closest('.window-frame')
        return window ? window.id : 'default-game'
    }
}

// Initialize when DOM ready
const gameOfLifeManager = new GameOfLifeManager()

// Global access for debugging
window.gameOfLifeManager = gameOfLifeManager