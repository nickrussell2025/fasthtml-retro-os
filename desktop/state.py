from fasthtml.common import *
from desktop.components import Desktop, Window


js_script = Script(src="/static/js/desktop.js")
app = FastHTML(hdrs=(Link(rel="stylesheet", href="/static/css/style.css"), js_script))


@app.get("/{fname:path}.{ext:static}")
def static_file(fname: str, ext: str):
    return FileResponse(f'{fname}.{ext}')


@app.get("/")
def home():
    return Desktop()


@app.post("/open")  # NEW ROUTE
def open_item(name: str, type: str, icon_x: int, icon_y: int):
    content = Div(f"{name} contents...")
    return Window(name, content, icon_x, icon_y)


@app.delete("/window/{window_id}")  # Also add this for closing windows
def close_window(window_id: str):
    return ""


@app.post("/window/{window_id}/minimize")
def minimize_window(window_id: str):
    # Return minimized version - just the titlebar
    return Div(
        Div(
            Span("📁", cls="minimized-icon"),  # Small icon
            Span(window_id.replace("win-", ""), cls="minimized-title"),
            Button("🔼", cls="restore-button",
                   hx_post=f"/window/{window_id}/restore",
                   hx_target=f"#{window_id}",
                   hx_swap="outerHTML"),
            cls="minimized-window"
        ),
        id=window_id,
        cls="minimized-container",
        style="position: absolute; left: 20px; bottom: 40px; z-index: 50;"
    )

@app.post("/window/{window_id}/maximize")
def maximize_window(window_id: str):
    # Return maximized window
    name = window_id.replace("win-", "").replace("-", " ")
    content = Div(f"{name} contents...")
    return Window(name, content, 0, 0, maximized=True)

@app.post("/window/{window_id}/restore")
def restore_window(window_id: str):
    # Return normal window
    name = window_id.replace("win-", "").replace("-", " ")
    content = Div(f"{name} contents...")
    return Window(name, content, 2, 2)  # Default position


serve()