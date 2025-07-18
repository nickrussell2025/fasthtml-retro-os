from fasthtml.common import (
    Button,
    Div,
    FastHTML,
    FileResponse,
    Link,
    Script,
    Span,
    serve,
)

from desktop.components import Desktop
from desktop.services import desktop_service
from desktop.state import window_manager, WINDOW_CONFIG


# Application setup
css_link = Link(rel="stylesheet", href="/static/css/style.css", type="text/css")
js_script = Script(src="/static/js/desktop.js")
app = FastHTML(hdrs=(css_link, js_script))

@app.get("/{fname:path}.{ext:static}")
def static_file(fname: str, ext: str):
    """Serve static files (CSS, JS, images)"""
    return FileResponse(f'{fname}.{ext}')

@app.get("/")
def home():
    """Main desktop view - force fresh state"""
    # Reset any stale window state
    window_manager.windows.clear()
    window_manager.open_folders.clear()
    window_manager.minimized_positions.clear()
    window_manager.available_positions = set(range(WINDOW_CONFIG['MAX_MINIMIZED']))
    
    return Desktop()

@app.post("/open")
def open_item(name: str, type: str, icon_x: int, icon_y: int):
    """Handle icon click - now uses service layer"""
    try:
        window, icon_update = desktop_service.open_item(name, type, icon_x, icon_y)
        
        if window is None:
            return ""
        
        if icon_update:
            return window, icon_update
        return window

    except Exception as e:
        print(f"ERROR in open_item: {e}")
        return Div(f"Error opening {name}: {str(e)}", cls="error-message")

    except Exception as e:
        print(f"ERROR in open_item: {e}")
        return Div(f"Error opening {name}: {str(e)}", cls="error-message")

@app.post("/window/{window_id}/minimize")
def minimize_window(window_id: str):
    """Minimize window to taskbar - now uses service"""
    try:
        result = desktop_service.minimize_window(window_id)
        return result if result else ""
    except Exception as e:
        print(f"ERROR in minimize_window: {e}")
        return ""

@app.post("/window/{window_id}/maximize")
def maximize_window(window_id: str):
    """Maximize window to full screen - now uses service"""
    try:
        result = desktop_service.maximize_window(window_id)
        return result if result else ""
    except Exception as e:
        print(f"ERROR in maximize_window: {e}")
        return ""

@app.post("/window/{window_id}/restore")
def restore_window(window_id: str):
    """Restore window from minimized or maximized state - now uses service"""
    try:
        result = desktop_service.restore_window(window_id)
        return result if result else ""
    except Exception as e:
        print(f"ERROR in restore_window: {e}")
        return ""

@app.delete("/window/{window_id}")
def close_window(window_id: str):
    """Close window and clean up state - now uses service"""
    try:
        icon_update = desktop_service.close_window(window_id)
        return icon_update if icon_update else ""
    except Exception as e:
        print(f"ERROR in close_window: {e}")
        return ""

@app.post("/window/{window_id}/move")
def move_window(window_id: str, x: int, y: int):
    """Update window position - now uses service"""
    try:
        success = desktop_service.move_window(window_id, x, y)
        return "" if success else "Error"
    except Exception as e:
        print(f"ERROR in move_window: {e}")
        return ""

if __name__ == "__main__":
    serve()