from fasthtml.common import *

css_link = Link(rel="stylesheet", href="style.css", type="text/css")

js = Script("""
let openWindows = {}; // Track open windows by folder name

function makeDraggable() {
    const windows = document.querySelectorAll('.window-frame');
    
    windows.forEach(window => {
        const titlebar = window.querySelector('.window-titlebar');
        let isDragging = false;
        let startX, startY, startLeft, startTop;
        
        titlebar.addEventListener('mousedown', (e) => {
            e.preventDefault();
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = window.offsetLeft;
            startTop = window.offsetTop;
            
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', stopDrag);
        });
        
        function drag(e) {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            window.style.left = (startLeft + dx) + 'px';
            window.style.top = (startTop + dy) + 'px';
        }
        
        function stopDrag() {
            isDragging = false;
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('mouseup', stopDrag);
        }
    });
}

function setupWindowControls() {
    document.addEventListener('click', (e) => {
        const window = e.target.closest('.window-frame');
        if (!window) return;
        
        // Minimize button
        if (e.target.classList.contains('min-btn')) {
            const windowTitle = window.querySelector('.window-title').textContent;
            const windowId = window.id;
            
            window.style.display = 'none';
            
            const taskbar = document.querySelector('.taskbar');
            const taskbarButton = document.createElement('button');
            taskbarButton.className = 'taskbar-button';
            taskbarButton.textContent = windowTitle;
            taskbarButton.dataset.windowId = windowId;
            
            const clock = document.querySelector('.taskbar-clock');
            taskbar.insertBefore(taskbarButton, clock);
            
            taskbarButton.addEventListener('click', () => {
                window.style.display = 'block';
                taskbarButton.remove();
            });
        }
        
        // Maximize button
        if (e.target.classList.contains('max-btn')) {
            if (window.classList.contains('maximized')) {
                window.classList.remove('maximized');
                window.style.width = '500px';
                window.style.height = '350px';
                window.style.top = '50px';
                window.style.left = '100px';
            } else {
                window.classList.add('maximized');
                window.style.width = 'calc(100vw - 20px)';
                window.style.height = 'calc(100vh - 80px)';
                window.style.top = '10px';
                window.style.left = '10px';
            }
        }
        
        // Close button
        if (e.target.classList.contains('close-btn')) {
            const windowTitle = window.querySelector('.window-title').textContent;
            
            // Remove from tracking
            delete openWindows[windowTitle];
            
            window.style.transform = 'scale(0)';
            window.style.opacity = '0';
            setTimeout(() => {
                window.remove();
            }, 200);
        }
    });
}

function setupDesktopIcons() {
    document.addEventListener('dblclick', (e) => {
        const icon = e.target.closest('.desktop-icon');
        if (icon) {
            const iconType = icon.dataset.type;
            const folderName = icon.querySelector('.icon-label').textContent;
            
            if (iconType === 'folder') {
                // Check if window already exists
                if (openWindows[folderName]) {
                    // Window exists, bring it to front and flash it
                    const existingWindow = openWindows[folderName];
                    existingWindow.style.display = 'block';
                    existingWindow.style.zIndex = '1000';
                    
                    // Flash effect
                    existingWindow.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        existingWindow.style.transform = 'scale(1)';
                    }, 100);
                } else {
                    // Create new window
                    createNewWindow(folderName);
                }
            }
        }
    });
}

function createNewWindow(folderName) {
    const desktop = document.querySelector('.desktop-container');
    const windowId = 'window-' + Date.now();
    
    const content = `
        <p>> Directory: C:\\\\Desktop\\\\${folderName}</p>
        <p>> </p>
        <p>> file1.txt</p>
        <p>> file2.txt</p>
        <p>> documents/</p>
        <p>> images/</p>
        <p>> programs/</p>
        <p>> readme.txt</p>
        <p>> </p>
        <p>> 4 files, 3 directories</p>
        <p>> </p>
        <p>> ${folderName} contents loaded successfully_</p>
    `;
    
    const newWindow = document.createElement('div');
    newWindow.className = 'window-frame';
    newWindow.id = windowId;
    newWindow.innerHTML = `
        <div class="window-titlebar">
            <span class="window-title">${folderName}</span>
            <div class="window-controls">
                <button class="min-btn">_</button>
                <button class="max-btn">□</button>
                <button class="close-btn">×</button>
            </div>
        </div>
        <div class="window-content">
            ${content}
        </div>
    `;
    
    // Random position
    newWindow.style.top = (Math.random() * 200 + 50) + 'px';
    newWindow.style.left = (Math.random() * 300 + 50) + 'px';
    newWindow.style.zIndex = '100';
    
    desktop.appendChild(newWindow);
    
    // Track this window
    openWindows[folderName] = newWindow;
    
    // Make new window draggable
    makeDraggable();
}

document.addEventListener('DOMContentLoaded', () => {
    makeDraggable();
    setupWindowControls();
    setupDesktopIcons();
});
""")

# Update app creation to include JS
app = FastHTML(hdrs=(css_link, js))

@app.get("/{fname:path}.{ext:static}")
def static_file(fname: str, ext: str):
    return FileResponse(f'{fname}.{ext}')

@app.get("/")
def home():
    # Desktop container
    desktop = Div(
    Div(
        Div("📁", cls="icon-symbol"),
        Div("My Documents", cls="icon-label"),  # Add cls="icon-label"
        cls="desktop-icon",
        **{"data-type": "folder"},
        style="top: 100px; left: 50px;"
    ),
    Div(
        Div("📁", cls="icon-symbol"),
        Div("Projects", cls="icon-label"),      # Another folder
        cls="desktop-icon",
        **{"data-type": "folder"},
        style="top: 100px; left: 150px;"
    ),
    cls="desktop"
)
    
    # Taskbar at bottom
    taskbar = Div(
        Div("RETRO OS", cls="taskbar-brand"),
        Div("12:34 AM", cls="taskbar-clock"),
        cls="taskbar"
    )
    
    # One window for now
    window = Div(
        # Title bar
        Div(
            Span("Terminal.exe", cls="window-title"),
            Div(
                Button("_", cls="min-btn"),
                Button("□", cls="max-btn"),
                Button("×", cls="close-btn"),
                cls="window-controls"
            ),
            cls="window-titlebar"
        ),
        # Content
        Div(
            P("> Welcome to RETRO OS"),
            P("> System initialized..."),
            P("> Loading drivers..."),
            P("> Memory check: OK"),
            P("> Network: Connected"),
            P("> Graphics: Initialized"),
            P("> Audio: Ready"),
            P("> File system: Mounted"),
            P("> Security: Active"),
            P("> Ready for input_"),
            P("> Type 'help' for commands"),
            P("> "),
            *[P(f"> Log entry {i}: System running normally") for i in range(1, 20)],
            cls="window-content"
        ),
        cls="window-frame",
        id="window1"
    )
    
    # Put window inside desktop
    desktop_with_window = Div(
        desktop,
        window,
        cls="desktop-container"
    )
    
    return Title("RETRO OS"), Div(
        desktop_with_window,
        taskbar,
        cls="os-container"
    )

serve()