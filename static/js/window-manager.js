class WindowManager {
    constructor() {
        this.zIndex = 100
        this.windows = new Map()
        this.taskbar = null
        this.isDragging = false
        
        this.setupEvents()
        console.log('WindowManager ready')
    }
    
    setupEvents() {
        // Handle all clicks - bring windows to front
        document.addEventListener('click', (e) => {
            const window = e.target.closest('.window-frame')
            if (window && !e.target.matches('button, input, select, textarea')) {
                this.focusWindow(window.id)
            }
        })
        
        // Handle window dragging
        document.addEventListener('mousedown', (e) => {
            const titlebar = e.target.closest('.window-titlebar')
            if (!titlebar || e.target.matches('button')) return
            
            const window = titlebar.closest('.window-frame')
            if (!window) return
            
            this.startDrag(window, e)
        })
        
        // Watch for new windows - no delays needed
        new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.classList?.contains('window-frame')) {
                        this.focusWindow(node.id)
                    }
                })
            })
        }).observe(document.body, { childList: true, subtree: true })
    }
    
    focusWindow(windowId) {
        const window = document.getElementById(windowId)
        if (!window || window.style.display === 'none') return
        
        // Actually set a high z-index
        this.zIndex += 10  // Bigger increment to ensure it's on top
        window.style.zIndex = this.zIndex
        
        console.log(`Window ${windowId} focused with z-index ${this.zIndex}`)
    }
    
    startDrag(window, e) {
        this.focusWindow(window.id)
        this.isDragging = true
        
        const startX = e.clientX - parseInt(window.style.left || 0)
        const startY = e.clientY - parseInt(window.style.top || 0)
        
        const onMove = (e) => {
            if (!this.isDragging) return
            window.style.left = (e.clientX - startX) + 'px'
            window.style.top = Math.max(0, e.clientY - startY) + 'px'
        }
        
        const onUp = () => {
            this.isDragging = false
            document.removeEventListener('mousemove', onMove)
            document.removeEventListener('mouseup', onUp)
        }
        
        document.addEventListener('mousemove', onMove)
        document.addEventListener('mouseup', onUp)
        e.preventDefault()
    }
    
    minimize(windowId) {
        const window = document.getElementById(windowId)
        if (!window) return
        
        const title = window.querySelector('.window-title')?.textContent || 'Window'
        window.style.display = 'none'
        this.addToTaskbar(windowId, title)
    }
    
    restore(windowId) {
        const window = document.getElementById(windowId)
        if (!window) return
        
        window.style.display = 'block'
        this.focusWindow(windowId)
        this.removeFromTaskbar(windowId)
    }
    
    maximize(windowId) {
        const window = document.getElementById(windowId)
        if (!window) return
        
        this.focusWindow(windowId)
        window.classList.toggle('window-maximized')
    }
    
    addToTaskbar(windowId, title) {
        if (!this.taskbar) {
            this.taskbar = document.createElement('div')
            this.taskbar.id = 'taskbar'
            this.taskbar.style.cssText = 'position: fixed; bottom: 20px; left: 20px; display: flex; flex-direction: column; gap: 5px; z-index: 10000;'
            document.body.appendChild(this.taskbar)
        }
        
        const item = document.createElement('div')
        item.id = `taskbar-${windowId}`
        item.style.cssText = 'background: var(--primary-color); color: var(--bg-black); padding: 5px 10px; border-radius: 3px; display: flex; align-items: center; gap: 10px; min-width: 200px; cursor: pointer; font-family: var(--system-font);'
        item.innerHTML = `<span>📁</span><span style="flex: 1;">${title}</span><span style="font-size: 16px;">↗️</span>`
        
        item.onclick = () => this.restore(windowId)
        this.taskbar.appendChild(item)
    }
    
    removeFromTaskbar(windowId) {
        const item = document.getElementById(`taskbar-${windowId}`)
        if (item) item.remove()
    }
    
    onWindowClosed(windowId) {
        this.removeFromTaskbar(windowId)
    }
}

const windowManager = new WindowManager()