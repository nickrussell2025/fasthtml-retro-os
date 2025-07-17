from fasthtml.common import *

css_link = Link(rel="stylesheet", href="/static/css/style.css", type="text/css")
app = FastHTML(hdrs=(css_link,))

@app.get("/static/{fname:path}")
def static_file(fname: str):
    return FileResponse(f'static/{fname}')

def make_icon(name, emoji, item_type):
    return Div(
        Div(emoji, cls="icon-symbol"),
        Div(name, cls="icon-label"),
        cls="desktop-icon",
        hx_post="/desktop/open",
        hx_vals=f'{{"item_type": "{item_type}", "item_name": "{name}"}}'
    )

@app.get("/")
def home():
    return Div(
        make_icon("Documents", "📁", "folder"),
        make_icon("Programs", "📁", "folder"),
        make_icon("Game of Life", "🎮", "program"),
        cls="desktop-container",
        id="desktop"
    )

@app.post("/desktop/open")
def open_item(item_type: str, item_name: str):
    return f"Opening {item_type}: {item_name}"

serve()