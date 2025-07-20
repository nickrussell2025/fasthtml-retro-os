class SettingsManager {
    constructor() {
        this.prefix = 'retro-os-'
        console.log('SettingsManager initialized')
    }
    
    save(key, value) {
        console.log('Saving setting:', key, '=', value)
        localStorage.setItem(this.prefix + key, JSON.stringify(value))
        this.applySetting(key, value)
    }
    
    load(key, defaultValue) {
        const stored = localStorage.getItem(this.prefix + key)
        const value = stored ? JSON.parse(stored) : defaultValue
        console.log('Loading setting:', key, '=', value)
        return value
    }
    
    loadAllOnStartup() {
        console.log('Loading all settings on startup...')
        const theme = this.load('theme_color', 'green')
        const font = this.load('font', 'courier')
        const scanlines = this.load('scanline_intensity', 0.12)
        
        this.applySetting('theme_color', theme)
        this.applySetting('font', font)
        this.applySetting('scanline_intensity', scanlines)
        
        console.log('Settings loaded:', { theme, font, scanlines })
    }
    
    applySetting(key, value) {
        switch(key) {
            case 'theme_color':
                this.applyTheme(value)
                break
            case 'font':
                this.applyFont(value)
                break
            case 'scanline_intensity':
                this.applyScanlines(value)
                break
        }
    }

    applyTheme(themeColor) {
        const hueMap = { 
            green: 120, cyan: 180, amber: 45, purple: 270,
            red: 348, orange: 24, pink: 328, lime: 120, blue: 210, white: 0
        }
        const hue = hueMap[themeColor] || 120
        
        let styleEl = document.getElementById('dynamic-theme')
        if (!styleEl) {
            styleEl = document.createElement('style')
            styleEl.id = 'dynamic-theme'
            document.head.appendChild(styleEl)
        }
        
        styleEl.textContent = `:root { --primary-hue: ${hue} !important; }`
        console.log('Applied theme:', themeColor, 'hue:', hue)
    }

    applyFont(font) {
        const fontMap = {
            courier: "'Courier New', monospace",
            monaco: "'Monaco', monospace", 
            consolas: "'Consolas', monospace",
            fira: "'Fira Code', 'Courier New', monospace",
            ubuntu: "'Ubuntu Mono', 'Courier New', monospace",
            source: "'Source Code Pro', 'Courier New', monospace",
            jetbrains: "'JetBrains Mono', 'Courier New', monospace",
            roboto: "'Roboto Mono', 'Courier New', monospace",
            inconsolata: "'Inconsolata', 'Courier New', monospace"
        }
        const fontFamily = fontMap[font] || fontMap.courier
        
        let styleEl = document.getElementById('dynamic-font')
        if (!styleEl) {
            styleEl = document.createElement('style')
            styleEl.id = 'dynamic-font'
            document.head.appendChild(styleEl)
        }
        
        styleEl.textContent = `:root { --system-font: ${fontFamily} !important; }`
        console.log('Applied font:', font, 'family:', fontFamily)
    }

    applyScanlines(intensity) {
        let styleEl = document.getElementById('dynamic-scanlines')
        if (!styleEl) {
            styleEl = document.createElement('style')
            styleEl.id = 'dynamic-scanlines'
            document.head.appendChild(styleEl)
        }
        
        styleEl.textContent = `:root { --scanline-opacity: ${intensity} !important; }`
        console.log('Applied scanlines:', intensity)
    }
}

// Create global instance with different name to avoid conflicts
const settingsManager = new SettingsManager()

// Load settings when page loads
window.addEventListener('load', () => {
    setTimeout(() => settingsManager.loadAllOnStartup(), 100)
})

console.log('NEW Settings manager ready')
