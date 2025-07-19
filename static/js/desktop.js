// Window dragging functionality
let isDragging = false;
let currentWindow = null;
let startX, startY, startLeft, startTop;

// Setup dragging for all windows
htmx.onLoad(function(element) {
    if (element.classList?.contains('window-frame')) {
        setupWindowDragging(element);
    }
});

function setupWindowDragging(windowElement) {
    const titlebar = windowElement.querySelector('.window-titlebar');
    
    titlebar.addEventListener('mousedown', (e) => {
        // Don't drag if clicking buttons
        if (e.target.tagName === 'BUTTON') return;
        
        isDragging = true;
        currentWindow = windowElement;
        
        startX = e.clientX;
        startY = e.clientY;
        startLeft = parseInt(windowElement.style.left);
        startTop = parseInt(windowElement.style.top);
        
        document.addEventListener('mousemove', handleDrag);
        document.addEventListener('mouseup', stopDrag);
    });
}

function handleDrag(e) {
    if (!isDragging) return;
    
    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;
    
    currentWindow.style.left = (startLeft + deltaX) + 'px';
    currentWindow.style.top = (startTop + deltaY) + 'px';
}

function stopDrag() {
    isDragging = false;
    currentWindow = null;
    document.removeEventListener('mousemove', handleDrag);
    document.removeEventListener('mouseup', stopDrag);
}

// Window focus - bring clicked window to front
document.addEventListener('click', function(e) {
    const windowElement = e.target.closest('.window-frame');
    
    if (windowElement && !e.target.matches('button')) {
        // Find highest current z-index and add 1
        const allWindows = document.querySelectorAll('.window-frame');
        let maxZ = 100;
        allWindows.forEach(win => {
            const z = parseInt(win.style.zIndex) || 100;
            if (z > maxZ) maxZ = z;
        });
        windowElement.style.zIndex = maxZ + 1;
    }
});