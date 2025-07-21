// CLEAN DESKTOP MANAGER - NO BLOAT, JUST WORKING FEATURES
console.log('Loading Clean Desktop Manager...')

let zIndex = 1000

// =============================================================================
// WAIT FOR DOM - SIMPLE CHECK
// =============================================================================

function init() {
    console.log('Desktop Manager Ready')
    
    // =============================================================================
    // WINDOW FOCUS - IMMEDIATE, NO DELAYS
    // =============================================================================
    
    // Watch for new windows
    new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.classList?.contains('window-frame')) {
                    // Force new window to front immediately
                    zIndex += 100
                    node.style.zIndex = zIndex
                    console.log('NEW WINDOW TO FRONT:', node.id)
                    
                    // Check for Game of Life immediately - no delays
                    checkForGame(node)
                }
            })
        })
    }).observe(document.body, { childList: true, subtree: true })
    
    // Click focus - simple and fast
    document.addEventListener('click', (e) => {
        const window = e.target.closest('.window-frame')
        if (window && !e.target.matches('button, input, select, textarea')) {
            zIndex += 10
            window.style.zIndex = zIndex
        }
    })
    
    // =============================================================================
    // WINDOW DRAGGING - OPTIMIZED FOR SMOOTHNESS
    // =============================================================================
    
    let isDragging = false
    let dragWindow = null
    
    document.addEventListener('mousedown', (e) => {
        const titlebar = e.target.closest('.window-titlebar')
        if (!titlebar || e.target.matches('button')) return
        
        const window = titlebar.closest('.window-frame')
        if (!window) return
        
        // Focus window
        zIndex += 10
        window.style.zIndex = zIndex
        
        // Start drag - calculate once
        isDragging = true
        dragWindow = window
        
        const rect = window.getBoundingClientRect()
        const offsetX = e.clientX - rect.left
        const offsetY = e.clientY - rect.top
        
        const handleMove = (e) => {
            if (!isDragging) return
            
            // Direct positioning - no calculations in loop
            dragWindow.style.left = (e.clientX - offsetX) + 'px'
            dragWindow.style.top = Math.max(0, e.clientY - offsetY) + 'px'
        }
        
        const handleStop = () => {
            isDragging = false
            dragWindow = null
            document.removeEventListener('mousemove', handleMove)
            document.removeEventListener('mouseup', handleStop)
        }
        
        document.addEventListener('mousemove', handleMove)
        document.addEventListener('mouseup', handleStop)
        e.preventDefault()
    })
    
    // =============================================================================
    // GAME OF LIFE - CLEAN HTMX INTEGRATION
    // =============================================================================
    
    let gameIntervals = new Map()
    
    // HTMX cleanup - disabled since inline script handles games
    // document.addEventListener('htmx:beforeSwap', (e) => {
    //     if (e.target.id === 'game-container') {
    //         stopGame(e.target)
    //     }
    // })
    
    // HTMX restart - disabled since inline script handles games  
    // document.addEventListener('htmx:afterSwap', (e) => {
    //     if (e.target.id === 'game-container') {
    //         checkForGame(e.target)
    //     }
    // })
    
    function checkForGame(container) {
        console.log('=== CHECKING FOR GAME ===')
        console.log('Container:', container)
        
        const gameStatus = container.querySelector('#game-status')
        console.log('Game status element:', gameStatus)
        
        if (!gameStatus) {
            console.log('NO GAME STATUS FOUND - not a game window')
            return
        }
        
        const statusText = gameStatus.textContent
        console.log('Status text:', statusText)
        
        const hasAutoRunning = statusText.includes('AUTO-RUNNING')
        console.log('Has AUTO-RUNNING:', hasAutoRunning)
        
        if (hasAutoRunning) {
            console.log('🎮 STARTING AUTO-RUN')
            startGame(container)
        } else {
            console.log('❌ Auto-run not active')
        }
    }
    
    function startGame(gameContainer) {
        const windowId = getWindowId(gameContainer)
        
        // Stop existing
        stopGame(gameContainer)
        
        // Get grid
        const gridElement = gameContainer.querySelector('#game-grid')
        if (!gridElement) {
            console.error('No game grid found')
            return
        }
        
        // Extract initial state
        let grid = extractGrid(gridElement)
        let generation = extractGeneration(gameContainer)
        
        console.log(`Game started: ${grid.length}x${grid[0]?.length}`)
        
        // Start interval
        const interval = setInterval(() => {
            grid = stepGame(grid)
            generation++
            updateDisplay(gameContainer, grid, generation)
        }, 500)
        
        gameIntervals.set(windowId, interval)
    }
    
    function stopGame(gameContainer) {
        const windowId = getWindowId(gameContainer)
        const interval = gameIntervals.get(windowId)
        
        if (interval) {
            clearInterval(interval)
            gameIntervals.delete(windowId)
            console.log('Game stopped:', windowId)
        }
    }
    
    function extractGrid(gridElement) {
        console.log('=== EXTRACTING GRID ===')
        console.log('Grid element:', gridElement)
        console.log('Grid children (rows):', gridElement.children.length)
        
        const rows = Array.from(gridElement.children)
        console.log('First row children (cells):', rows[0]?.children.length)
        
        const grid = rows.map((row, y) => {
            const cells = Array.from(row.children)
            return cells.map((cell, x) => {
                const bg = cell.style.background
                const isAlive = bg.includes('var(--primary-color)') || 
                               (bg !== 'transparent' && bg !== '')
                return isAlive
            })
        })
        
        console.log('Extracted grid:', grid.length, 'x', grid[0]?.length)
        console.log('First few rows:', grid.slice(0, 3))
        return grid
    }
    
    function extractGeneration(gameContainer) {
        const statusText = gameContainer.querySelector('#game-status')?.textContent || ''
        const match = statusText.match(/Generation: (\d+)/)
        return match ? parseInt(match[1]) : 0
    }
    
    function stepGame(grid) {
        const height = grid.length
        const width = grid[0]?.length || 0
        const newGrid = Array(height).fill().map(() => Array(width).fill(false))
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const neighbors = countNeighbors(grid, x, y, width, height)
                const isAlive = grid[y][x]
                
                if (isAlive && (neighbors === 2 || neighbors === 3)) {
                    newGrid[y][x] = true
                } else if (!isAlive && neighbors === 3) {
                    newGrid[y][x] = true
                }
            }
        }
        
        return newGrid
    }
    
    function countNeighbors(grid, x, y, width, height) {
        let count = 0
        for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
                if (dx === 0 && dy === 0) continue
                const ny = y + dy
                const nx = x + dx
                if (ny >= 0 && ny < height && nx >= 0 && nx < width && grid[ny][nx]) {
                    count++
                }
            }
        }
        return count
    }
    
    function updateDisplay(gameContainer, grid, generation) {
        const statusElement = gameContainer.querySelector('#game-status')
        const gridElement = gameContainer.querySelector('#game-grid')
        
        if (statusElement) {
            const liveCount = grid.flat().filter(cell => cell).length
            statusElement.textContent = `Generation: ${generation} • Live cells: ${liveCount} • AUTO-RUNNING`
        }
        
        if (gridElement) {
            const rows = gridElement.children
            for (let y = 0; y < grid.length && y < rows.length; y++) {
                const cells = rows[y].children
                for (let x = 0; x < grid[y].length && x < cells.length; x++) {
                    cells[x].style.background = grid[y][x] ? 'var(--primary-color)' : 'transparent'
                }
            }
        }
    }
    
    function getWindowId(gameContainer) {
        const window = gameContainer.closest('.window-frame')
        return window ? window.id : 'default-game'
    }
    
    // =============================================================================
    // WINDOW OPERATIONS - SIMPLE
    // =============================================================================
    
    window.windowManager = {
        minimize: (windowId) => {
            const window = document.getElementById(windowId)
            if (!window) return
            
            window.style.display = 'none'
            addToTaskbar(windowId, window.querySelector('.window-title')?.textContent || 'Window')
            
            // Stop any game
            const gameContainer = window.querySelector('#game-container')
            if (gameContainer) stopGame(gameContainer)
        },
        
        restore: (windowId) => {
            const window = document.getElementById(windowId)
            if (!window) return
            
            window.style.display = 'block'
            zIndex += 10
            window.style.zIndex = zIndex
            removeFromTaskbar(windowId)
            
            // Restart any game
            const gameContainer = window.querySelector('#game-container')
            if (gameContainer) checkForGame(gameContainer)
        },
        
        maximize: (windowId) => {
            const window = document.getElementById(windowId)
            if (!window) return
            
            zIndex += 10
            window.style.zIndex = zIndex
            window.classList.toggle('window-maximized')
        },
        
        onWindowClosed: (windowId) => {
            removeFromTaskbar(windowId)
            
            // Clean up game
            const interval = gameIntervals.get(windowId)
            if (interval) {
                clearInterval(interval)
                gameIntervals.delete(windowId)
            }
        }
    }
    
    function addToTaskbar(windowId, title) {
        let taskbar = document.getElementById('desktop-taskbar')
        if (!taskbar) {
            taskbar = document.createElement('div')
            taskbar.id = 'desktop-taskbar'
            taskbar.style.cssText = 'position: fixed; bottom: 20px; left: 20px; display: flex; flex-direction: column; gap: 5px; z-index: 10000;'
            document.body.appendChild(taskbar)
        }
        
        const item = document.createElement('div')
        item.id = `taskbar-${windowId}`
        item.style.cssText = 'background: var(--primary-color); color: var(--bg-black); padding: 5px 10px; border-radius: 3px; display: flex; align-items: center; gap: 10px; min-width: 200px; cursor: pointer; font-family: var(--system-font);'
        
        item.innerHTML = `
            <span class="minimized-icon">
                <img src="/static/icons/folder.svg" alt="window" class="window-control-svg" style="width: 16px; height: 16px;">
            </span>
            <span style="flex: 1;">${title}</span>
            <span class="minimized-icon">
                <img src="/static/icons/circle-chevron-up.svg" alt="restore" class="window-control-svg" style="width: 16px; height: 16px;">
            </span>
        `
        
        item.onclick = () => window.windowManager.restore(windowId)
        taskbar.appendChild(item)
    }
    
    function removeFromTaskbar(windowId) {
        const item = document.getElementById(`taskbar-${windowId}`)
        if (item) item.remove()
    }
    
    console.log('Desktop Manager initialized - all features ready')
}

// Initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
} else {
    init()
}