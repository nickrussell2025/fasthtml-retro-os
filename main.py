from fasthtml.common import (
    Div,
    FastHTML,
    FileResponse,
    Link,
    Script,
    serve,
)

from desktop.components import Desktop
from desktop.services import desktop_service
from desktop.state import WINDOW_CONFIG, window_manager

# Application setup
css_link = Link(rel="stylesheet", href="/static/css/style.css", type="text/css")
js_script = Script(src="/static/js/desktop.js")
app = FastHTML(hdrs=(css_link, js_script))


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

@app.get("/favicon.ico")
def favicon():
    import os
    print("Favicon requested!")
    print("File exists:", os.path.exists("static/favicon.ico"))
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    else:
        return "FAVICON FILE NOT FOUND"

@app.get("/static/{filepath:path}")
def static_files(filepath: str):
    return FileResponse(f"static/{filepath}")

@app.post("/settings/theme")
def update_theme(theme_color: str):
    return desktop_service.update_theme(theme_color)

@app.post("/settings/font")
def update_font(font: str):
    return desktop_service.update_font(font)

@app.post("/settings/scanlines")
def update_scanlines(scanline_intensity: float):
    return desktop_service.update_scanlines(scanline_intensity)

if __name__ == "__main__":
    serve()
