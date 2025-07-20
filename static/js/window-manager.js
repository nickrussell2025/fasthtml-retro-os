class WindowManager {
    constructor() {
        this.windows = new Map()        // Track active windows
        this.zIndex = 100              // For bringing windows to front
        this.taskbarItems = new Map()  // Track minimized windows
        console.log('WindowManager constructor called')
    }
    
    minimize(windowId) {
        console.log('Minimizing window:', windowId)
        
        const windowElement = document.getElementById(windowId)
        if (!windowElement) {
            console.warn('Window not found:', windowId)
            return false
        }
        
        // Get window title
        const title = windowElement.querySelector('.window-title')?.textContent || 'Window'
        
        // Store the window's current state
        this.windows.set(windowId, {
            display: windowElement.style.display,
            zIndex: windowElement.style.zIndex,
            title: title
        })
        
        // Hide the window
        windowElement.style.display = 'none'
        
        // Add to taskbar
        this.addToTaskbar(windowId, title)
        
        console.log('Window minimized successfully')
        return true
    }
    
    restore(windowId) {
        console.log('Restoring window:', windowId)
        
        const windowElement = document.getElementById(windowId)
        if (!windowElement) {
            console.warn('Window not found:', windowId)
            return false
        }
        
        // Show the window
        windowElement.style.display = 'block'
        windowElement.style.zIndex = ++this.zIndex  // Bring to front
        
        // Remove from taskbar
        this.removeFromTaskbar(windowId)
        
        console.log('Window restored successfully')
        return true
    }
    
    maximize(windowId) {
        console.log('Maximizing window:', windowId)
        
        const windowElement = document.getElementById(windowId)
        if (!windowElement) {
            console.warn('Window not found:', windowId)
            return false
        }
        
        // Toggle maximize state
        if (windowElement.classList.contains('window-maximized')) {
            windowElement.classList.remove('window-maximized')
        } else {
            windowElement.classList.add('window-maximized')
        }
        
        console.log('Window maximized successfully')
        return true
    }
    
    addToTaskbar(windowId, title) {
        // Find or create taskbar container
        let taskbar = document.getElementById('taskbar')
        if (!taskbar) {
            taskbar = document.createElement('div')
            taskbar.id = 'taskbar'
            taskbar.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 20px;
                display: flex;
                flex-direction: column;
                gap: 5px;
                z-index: 1000;
            `
            document.body.appendChild(taskbar)
        }
        
        // Create taskbar item with icon
        const item = document.createElement('div')
        item.id = `taskbar-${windowId}`
        item.style.cssText = `
            background: var(--primary-color);
            color: var(--bg-black);
            padding: 5px 10px;
            border-radius: 3px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            min-width: 200px;
            font-family: var(--system-font);
        `
        
        // Get window icon and restore icon (black for visibility against green background)
        const windowIconHtml = '<img src="/static/icons/folder.svg" alt="window" class="window-control-svg" style="width: 16px; height: 16px; filter: brightness(0); vertical-align: middle;">'
        const restoreIconHtml = '<img src="/static/icons/circle-chevron-up.svg" alt="restore" class="window-control-svg" style="width: 12px; height: 12px; filter: brightness(0); vertical-align: middle; cursor: pointer;">'
        
        item.innerHTML = `
            <span class="minimized-icon" style="display: inline-flex; align-items: center;">${windowIconHtml}</span>
            <span class="minimized-title" style="flex: 1;">${title}</span>
            <button class="restore-button" onclick="windowManager.restore('${windowId}')" 
                    style="background: none; border: none; padding: 2px; margin: 0; cursor: pointer;">${restoreIconHtml}</button>
        `
        
        taskbar.appendChild(item)
        this.taskbarItems.set(windowId, item)
    }
    
    removeFromTaskbar(windowId) {
        const item = this.taskbarItems.get(windowId)
        if (item) {
            item.remove()
            this.taskbarItems.delete(windowId)
        }
        
        // Clean up window state
        this.windows.delete(windowId)
    }
    
    // Helper method to bring window to front when clicked
    focusWindow(windowId) {
        const windowElement = document.getElementById(windowId)
        if (windowElement && windowElement.style.display !== 'none') {
            windowElement.style.zIndex = ++this.zIndex
        }
    }
}

// Create global instance
const windowManager = new WindowManager()

// Add click listener to bring windows to front when clicked
document.addEventListener('click', (e) => {
    const windowElement = e.target.closest('.window-frame')
    if (windowElement && !e.target.matches('button')) {
        windowManager.focusWindow(windowElement.id)
    }
})

console.log('WindowManager initialized successfully')

// Settings Manager - added to existing working file
// class SettingsManager {
//     constructor() {
//         this.prefix = 'retro-os-'
//         console.log('SettingsManager initialized')
//     }
    
//     save(key, value) {
//         console.log('Saving setting:', key, '=', value)
//         localStorage.setItem(this.prefix + key, JSON.stringify(value))
//         this.applySetting(key, value)
//     }
    
//     load(key, defaultValue) {
//         const stored = localStorage.getItem(this.prefix + key)
//         const value = stored ? JSON.parse(stored) : defaultValue
//         console.log('Loading setting:', key, '=', value)
//         return value
//     }
    
//     loadAllOnStartup() {
//         console.log('Loading all settings on startup...')
//         const theme = this.load('theme_color', 'green')
//         const font = this.load('font', 'courier')
//         const scanlines = this.load('scanline_intensity', 0.12)
        
//         this.applySetting('theme_color', theme)
//         this.applySetting('font', font)
//         this.applySetting('scanline_intensity', scanlines)
        
//         console.log('Settings loaded:', { theme, font, scanlines })
//     }
    
// applySetting(key, value) {
//     switch(key) {
//         case 'theme_color':
//             this.applyTheme(value)
//             break
//         case 'font':
//             this.applyFont(value)
//             break
//         case 'scanline_intensity':
//             this.applyScanlines(value)
//             break
//     }
// }

// applyTheme(themeColor) {
//     const hueMap = { green: 120, cyan: 180, amber: 45, purple: 270 }
//     const hue = hueMap[themeColor] || 120
    
//     let styleEl = document.getElementById('dynamic-theme')
//     if (!styleEl) {
//         styleEl = document.createElement('style')
//         styleEl.id = 'dynamic-theme'
//         document.head.appendChild(styleEl)
//     }
    
//     styleEl.textContent = `:root { --primary-hue: ${hue} !important; }`
//     console.log('Applied theme:', themeColor, 'hue:', hue)
// }

//     applyFont(font) {
//         const fontMap = {
//             courier: "'Courier New', monospace",
//             monaco: "'Monaco', monospace", 
//             consolas: "'Consolas', monospace"
//         }
//         const fontFamily = fontMap[font] || fontMap.courier
        
//         let styleEl = document.getElementById('dynamic-font')
//         if (!styleEl) {
//             styleEl = document.createElement('style')
//             styleEl.id = 'dynamic-font'
//             document.head.appendChild(styleEl)
//         }
        
//         styleEl.textContent = `:root { --system-font: ${fontFamily} !important; }`
//         console.log('Applied font:', font, 'family:', fontFamily)
//     }

//     applyScanlines(intensity) {
//         let styleEl = document.getElementById('dynamic-scanlines')
//         if (!styleEl) {
//             styleEl = document.createElement('style')
//             styleEl.id = 'dynamic-scanlines'
//             document.head.appendChild(styleEl)
//         }
        
//         styleEl.textContent = `:root { --scanline-opacity: ${intensity} !important; }`
//         console.log('Applied scanlines:', intensity)
//     }
// }

// // Create settings manager instance
// const settingsManager = new SettingsManager()

// // Load settings when page loads
// window.addEventListener('load', () => {
//     setTimeout(() => settingsManager.loadAllOnStartup(), 100)
// })

// console.log('Settings manager added to window-manager.js')