# main.py - Fixed imports and removed broken game-manager.js

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

from programs.game_of_life.routes import setup_gameoflife_routes

# Application setup - REMOVED broken game-manager.js 
css_link = Link(rel="stylesheet", href="/static/css/style.css", type="text/css")
desktop_manager_script = Script(src="/static/js/desktop-manager.js")
settings_manager_script = Script(src="/static/js/settings-manager.js")

app = FastHTML(hdrs=(css_link, desktop_manager_script, settings_manager_script))

# Setup routes
setup_gameoflife_routes(app)

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
    """Handle icon click"""
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

@app.delete("/window/{window_id}")
def close_window(window_id: str):
    """Close window and clean up state"""
    try:
        icon_update = desktop_service.close_window(window_id)
        return icon_update if icon_update else ""
    except Exception as e:
        print(f"ERROR in close_window: {e}")
        return ""

@app.post("/window/{window_id}/move")
def move_window(window_id: str, x: int, y: int):
    """Update window position"""
    try:
        success = desktop_service.move_window(window_id, x, y)
        return "" if success else "Error"
    except Exception as e:
        print(f"ERROR in move_window: {e}")
        return ""

@app.get("/static/{path:path}")
def static_files(path: str):
    """Serve static files"""
    return FileResponse(f'static/{path}')

if __name__ == "__main__":
    serve()