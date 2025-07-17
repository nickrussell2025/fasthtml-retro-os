from fasthtml.common import *
from desktop.components import Desktop, Window, CreateContent, wm  # Changed CreateRichContent to CreateContent

js_script = Script(src="/static/js/desktop.js")
app = FastHTML(hdrs=(Link(rel="stylesheet", href="/static/css/style.css"), js_script))

@app.get("/{fname:path}.{ext:static}")
def static_file(fname: str, ext: str):
    return FileResponse(f'{fname}.{ext}')

@app.get("/")
def home():
    return Desktop()

@app.post("/open")
def open_item(name: str, type: str, icon_x: int, icon_y: int):
    print(f"DEBUG: Opening {name}, type: {type}, x: {icon_x}, y: {icon_y}")
    
    content = CreateContent(name, type)
    print(f"DEBUG: Content created: {content}")
    
    window_id = wm.create_window(name, content, icon_x, icon_y)
    print(f"DEBUG: Window ID: {window_id}")
    
    if window_id is None:
        print("DEBUG: Window ID is None - already exists")
        return ""
    
    print("DEBUG: About to return Window")
    return Window(name, content, icon_x, icon_y)

@app.post("/window/{window_id}/minimize")
def minimize_window(window_id: str):
    position = wm.minimize_window(window_id)
    if position is None:
        return ""
        
    window_data = wm.get_window(window_id)  # Changed get_window_data to get_window
    
    bottom = 40 + (position * 30)
    
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
        style=f"position: absolute; left: 20px; bottom: {bottom}px; z-index: 50;"
    )

@app.post("/window/{window_id}/maximize")
def maximize_window(window_id: str):
    window_data = wm.maximize_window(window_id)
    if window_data:
        return Window(window_data['name'], window_data['content'], 0, 0, maximized=True)
    return ""

@app.post("/window/{window_id}/restore")
def restore_window(window_id: str):
    window_data = wm.restore_window(window_id)
    if window_data:
        x, y = window_data['position']
        return Window(window_data['name'], window_data['content'], x//120, y//120)
    return ""

@app.delete("/window/{window_id}")
def close_window(window_id: str):
    window_data = wm.get_window(window_id)  # Changed get_window_data to get_window
    
    if window_data:
        wm.close_folder(window_data['name'])
    
    wm.close_window(window_id)
    return Div(hx_get="/refresh-desktop", hx_target="#desktop", hx_swap="innerHTML")

@app.get("/refresh-desktop")
def refresh_desktop():
    """Return updated desktop with correct icon states"""
    return Desktop()

# New route for tracking window drags
@app.post("/window/{window_id}/move")
def move_window(window_id: str, x: int, y: int):
    wm.update_window_position(window_id, x, y)
    return ""

serve()