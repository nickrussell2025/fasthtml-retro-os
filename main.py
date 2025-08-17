# main.py - Fixed imports and removed broken game-manager.js

from fasthtml.common import (
    Div,
    FastHTML,
    FileResponse,
    Link,
    Script,
    serve,
    H2,
    Button,
    H3,
    P,
)

from desktop.components import Desktop
from desktop.services import desktop_service
from desktop.state import WINDOW_CONFIG, window_manager

from programs.game_of_life.routes import setup_gameoflife_routes

from programs.ereader.routes import setup_ereader_routes


# Application setup
css_link = Link(rel="stylesheet", href="/static/css/style.css", type="text/css")
desktop_manager_script = Script(src="/static/js/desktop-manager.js")
settings_manager_script = Script(src="/static/js/settings-manager.js")
ereader_script = Script(src="/static/js/ereader.js")
highlights_script = Script(src="/static/js/highlights-viewer.js")

app = FastHTML(hdrs=(css_link, desktop_manager_script, settings_manager_script, ereader_script, highlights_script))

# Setup program routes
setup_gameoflife_routes(app)
setup_ereader_routes(app)

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
        # Force clear any existing window state
        window_id = f"win-{name.replace(' ', '-').lower()}"
        window_manager.windows.pop(window_id, None)  # Remove if exists
        if name in ['Documents', 'Programs']:
            window_manager.close_folder(name)  # Mark folder as closed
        
        window, icon_update = desktop_service.open_item(name, type, icon_x, icon_y)
        
        if window is None:
            return ""

        if icon_update:
            return window, icon_update
        return window

    except Exception as e:
        print(f"ERROR in open_item: {e}")
        return Div(f"Error opening {name}: {str(e)}", cls="error-message")


@app.post("/window/{window_id}/move")
def move_window(window_id: str, x: int, y: int):
    """Update window position"""
    try:
        success = desktop_service.move_window(window_id, x, y)
        return "" if success else "Error"
    except Exception as e:
        print(f"ERROR in move_window: {e}")
        return ""

@app.get("/favicon.ico")
def favicon():
    import os
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for file at: {os.path.abspath('static/favicon.ico')}")
    print(f"File exists: {os.path.exists('static/favicon.ico')}")
    return FileResponse('static/favicon.ico')

@app.get("/{fname:path}.{ext:static}")
def static_file(fname: str, ext: str):
    """Serve static files with proper extension handling"""
    return FileResponse(f'{fname}.{ext}')


@app.get("/ereader/library")
def show_library():
    """Return library view - Feature 2 entry point"""
    from programs.ereader.library import LibraryView
    return LibraryView()

@app.post("/ereader/open") 
def open_book(book_id: str):
    """Open specific book - Feature 2 book launcher"""
    from programs.ereader.ereader import EReaderProgram
    program = EReaderProgram()
    return program.get_window_content(book_id=book_id)

# Add this section after your existing routes in main.py

import psutil
import os
import gc

@app.get("/debug/memory")
def memory_stats():
    """Basic memory monitoring endpoint"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return Div(
        H2("🔍 Memory Stats"),
        P(f"Physical RAM: {round(memory_info.rss / 1024 / 1024, 2)} MB"),
        P(f"Virtual Memory: {round(memory_info.vms / 1024 / 1024, 2)} MB"),
        P(f"Memory %: {round(process.memory_percent(), 2)}%"),
        P(f"Python Objects: {len(gc.get_objects()):,}"),
        P(f"Threads: {process.num_threads()}"),
        style="padding: 20px; font-family: var(--system-font);"
    )

@app.get("/debug/fast-test")
def fast_test():
    """Test FastHTML raw speed"""
    return Div("Fast response", style="padding: 20px;")

@app.post("/debug/simple-post")
def simple_post_test():
    """Test raw POST performance"""
    return Div("Simple POST response")

if __name__ == "__main__":
    import os
    import uvicorn
    
    # Environment detection
    is_production = bool(os.environ.get("RAILWAY_ENVIRONMENT_NAME") or 
                        os.environ.get("RENDER") or 
                        os.environ.get("VERCEL") or
                        os.environ.get("FLY_APP_NAME") or
                        os.environ.get("ENVIRONMENT") == "production")
    
    # Port configuration
    port = int(os.environ.get("PORT", 8000))
    
    if is_production:
        # Production configuration
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    else:
        # Local development configuration
        print(f"🚀 FastHTML Development Server")
        print(f"📍 Local: http://127.0.0.1:{port}")
        print(f"🌐 Network: http://0.0.0.0:{port}")
        print(f"🔄 Hot reload: enabled")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="debug"
        )