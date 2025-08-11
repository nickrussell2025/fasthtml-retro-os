// CLEAN DESKTOP MANAGER - WINDOWS ONLY

let zIndex = 1000

function isMobile() {
    return window.innerWidth <= 768
}

function init() {
    
    // =============================================================================
    // WINDOW FOCUS - NEW WINDOWS TO FRONT
    // =============================================================================
    
    new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.classList?.contains('window-frame')) {
                    zIndex += 100
                    node.style.zIndex = zIndex
                    
                    if (!isMobile()) {
                        node.style.position = 'absolute'
                    }
                    
                }
            })
        })
    }).observe(document.body, { childList: true, subtree: true })
    
    // Click focus
    document.addEventListener('click', (e) => {
        const window = e.target.closest('.window-frame')
        if (window && !e.target.matches('button, input, select, textarea')) {
            zIndex += 10
            window.style.zIndex = zIndex
        }
    })
    
    // =============================================================================
    // WINDOW DRAGGING
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
        
        // Skip dragging on mobile
        if (isMobile()) return
        
        // Start drag
        isDragging = true
        dragWindow = window
        
        const rect = window.getBoundingClientRect()
        const offsetX = e.clientX - rect.left
        const offsetY = e.clientY - rect.top
        
        const handleMove = (e) => {
            if (!isDragging) return
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
    // WINDOW OPERATIONS
    // =============================================================================
    
    window.windowManager = {
        minimize: (windowId) => {
            const window = document.getElementById(windowId)
            if (!window) return
            
            window.style.display = 'none'
            addToTaskbar(windowId, window.querySelector('.window-title')?.textContent || 'Window')
        },
        
        restore: (windowId) => {
            const window = document.getElementById(windowId)
            if (!window) return
            
            window.style.display = 'block'
            zIndex += 10
            window.style.zIndex = zIndex
            removeFromTaskbar(windowId)
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
    
}

// Initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
} else {
    init()
}

// Orientation and resize handling
window.addEventListener('orientationchange', function() {
    setTimeout(function() {
        document.body.style.height = window.innerHeight + 'px';
        window.dispatchEvent(new Event('resize'));
        
        const desktop = document.querySelector('.desktop-container');
        if (desktop) {
            desktop.style.height = window.innerHeight + 'px';
            desktop.style.width = window.innerWidth + 'px';
        }
    }, 100);
});

window.addEventListener('resize', function() {
    const desktop = document.querySelector('.desktop-container');
    if (desktop && window.innerWidth <= 768) {
        desktop.style.height = window.innerHeight + 'px';
        desktop.style.width = window.innerWidth + 'px';
    }
});