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

from desktop.components import CreateContent, Desktop, DesktopIcon, Window
from desktop.state import ICON_POSITIONS, window_manager

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
    """Main desktop view"""
    return Desktop()

@app.post("/open")
def open_item(name: str, type: str, icon_x: int, icon_y: int):
    """Handle icon click to open window with icon state update"""
    try:
        # Create content and window
        content = CreateContent(name, type)
        window_data = window_manager.create_window(name, content, icon_x, icon_y)

        if window_data is None:
            return ""  # Window already exists

        # Create window component
        window = Window(window_data)

        # For folders, also return updated icon via OOB
        if type == "folder":
            updated_icon = DesktopIcon(name, type, oob_update=True)
            return window, updated_icon

        return window

    except Exception as e:
        print(f"ERROR in open_item: {e}")
        return Div(f"Error opening {name}: {str(e)}", cls="error-message")

@app.post("/window/{window_id}/minimize")
def minimize_window(window_id: str):
    """Minimize window to taskbar"""
    try:
        position = window_manager.minimize_window(window_id)
        window_data = window_manager.get_window(window_id)

        if not window_data or position is None:
            return ""

        # Calculate taskbar position using configuration
        left, bottom = window_manager.calculate_taskbar_position(position)

        return Div(
            Div(
                Span("■", cls="minimized-icon"),
                Span(window_data['name'], cls="minimized-title"),
                Button("^", cls="restore-button",
                       hx_post=f"/window/{window_id}/restore",
                       hx_target=f"#{window_id}",
                       hx_swap="outerHTML"),
                cls="minimized-window"
            ),
            id=window_id,
            cls="minimized-container",
            style=f"position: absolute; left: {left}px; bottom: {bottom}px; z-index: 50;"
        )
    except Exception as e:
        print(f"ERROR in minimize_window: {e}")
        return ""

@app.post("/window/{window_id}/maximize")
def maximize_window(window_id: str):
    """Maximize window to full screen"""
    try:
        window_data = window_manager.maximize_window(window_id)
        return Window(window_data, maximized=True) if window_data else ""
    except Exception as e:
        print(f"ERROR in maximize_window: {e}")
        return ""

@app.post("/window/{window_id}/restore")
def restore_window(window_id: str):
    """Restore window from minimized or maximized state"""
    try:
        window_data = window_manager.restore_window(window_id)
        return Window(window_data) if window_data else ""
    except Exception as e:
        print(f"ERROR in restore_window: {e}")
        return ""

@app.delete("/window/{window_id}")
def close_window(window_id: str):
    """Close window and clean up state with icon update"""
    try:
        # Clean up window state
        closed_window_data = window_manager.close_window(window_id)

        # If folder was closed, return updated icon via OOB
        if (closed_window_data and
            closed_window_data.get('item_type') == 'folder' and
            closed_window_data['name'] in ICON_POSITIONS):

            return DesktopIcon(closed_window_data['name'], 'folder', oob_update=True)

        return ""

    except Exception as e:
        print(f"ERROR in close_window: {e}")
        return ""

@app.post("/window/{window_id}/move")
def move_window(window_id: str, x: int, y: int):
    """Update window position (called by JavaScript drag handler)"""
    try:
        window_manager.update_window_position(window_id, x, y)
        return ""
    except Exception as e:
        print(f"ERROR in move_window: {e}")
        return ""

if __name__ == "__main__":
    serve()
