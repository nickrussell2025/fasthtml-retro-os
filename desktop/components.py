from fasthtml.common import *

class WindowManager:
    def __init__(self):
        self.windows = {}
        self.minimized_positions = {}
        self.available_positions = set(range(10))
        self.next_z_index = 100
        self.open_folders = set()
        
    def create_window(self, name, content, icon_x, icon_y):
        window_id = f"win-{name.replace(' ', '-').lower()}"
        
        if window_id in self.windows:
            return None  # Already exists
            
        x = (icon_x * 120) + 150
        y = (icon_y * 120) + 50
        
        self.windows[window_id] = {
            'name': name,
            'content': content,
            'position': (x, y),
            'z_index': self.next_z_index,
            'maximized': False
        }
        self.next_z_index += 1
        return window_id
        
    def get_window(self, window_id):
        return self.windows.get(window_id)
        
    def minimize_window(self, window_id):
        if window_id not in self.windows or not self.available_positions:
            return 0
        position = min(self.available_positions)
        self.available_positions.remove(position)
        self.minimized_positions[window_id] = position
        return position
        
    def restore_window(self, window_id):
        if window_id in self.minimized_positions:
            pos = self.minimized_positions.pop(window_id)
            self.available_positions.add(pos)
        if window_id in self.windows:
            self.windows[window_id]['maximized'] = False
        return self.windows.get(window_id)
        
    def maximize_window(self, window_id):
        if window_id in self.windows:
            self.windows[window_id]['maximized'] = True
        return self.windows.get(window_id)
        
    def close_window(self, window_id):
        if window_id in self.minimized_positions:
            pos = self.minimized_positions.pop(window_id)
            self.available_positions.add(pos)
        self.windows.pop(window_id, None)
        
    def open_folder(self, name):
        self.open_folders.add(name)
        
    def close_folder(self, name):
        self.open_folders.discard(name)
        
    def is_folder_open(self, name):
        return name in self.open_folders

wm = WindowManager()

def Window(window_data, maximized=False):
    """Render window from window data"""
    if maximized or window_data.get('maximized', False):
        style = "position: absolute; left: 0; top: 0; width: 100vw; height: 100vh;"
    else:
        x, y = window_data['position']
        z = window_data['z_index']
        style = f"position: absolute; left: {x}px; top: {y}px; z-index: {z};"
    
    window_id = f"win-{window_data['name'].replace(' ', '-').lower()}"
    
    return Div(
        Div(
            Span(window_data['name'], cls="window-title"),
            Div(
                Button("▼", cls="window-minimize", 
                       hx_post=f"/window/{window_id}/minimize",
                       hx_target=f"#{window_id}",
                       hx_swap="outerHTML"),
                Button("▲", cls="window-maximize",
                       hx_post=f"/window/{window_id}/maximize", 
                       hx_target=f"#{window_id}",
                       hx_swap="outerHTML"),
                Button("■", cls="window-close", 
                       hx_delete=f"/window/{window_id}", 
                       hx_target=f"#{window_id}", 
                       hx_swap="outerHTML"),
                cls="window-controls"
            ),
            cls="window-titlebar"
        ),
        Div(window_data['content'], cls="window-content"),
        cls="window-frame",
        id=window_id,
        style=style
    )

def CreateContent(name, item_type):
    """Create window content"""
    if item_type == "folder":
        files = {
            "Documents": ["📄 resume.txt", "📄 notes.txt", "📁 projects/"],
            "Programs": ["🎮 Game of Life", "🧮 Calculator"]
        }.get(name, ["Empty folder"])
        
        return Div(*[Div(f, cls="file-item") for f in files], cls="file-explorer")
    
    elif item_type == "program" and name == "Game of Life":
        return Div(
            H3("Conway's Game of Life"),
            Div("🟩🟩⬜⬜🟩", cls="game-preview"),
            Div(
                Button("▶️ Play", cls="game-btn"),
                Button("⏸️ Pause", cls="game-btn"),
                Button("🔄 Reset", cls="game-btn"),
                cls="game-controls"
            ),
            cls="game-interface"
        )
    else:
        return Div(f"{name} interface", cls="program-content")

def DesktopIcon(name, item_type, x, y):
    icon = "🗁" if (item_type == "folder" and wm.is_folder_open(name)) else {
        "folder": "🗀", "program": "⚏"
    }.get(item_type, "🗎")
        
    return Div(
        Div(icon, cls="icon-symbol"),
        Div(name, cls="icon-label"),
        cls="desktop-icon",
        style=f"grid-column: {x}; grid-row: {y};",
        hx_post="/open",
        hx_vals=f'{{"name": "{name}", "type": "{item_type}", "icon_x": "{x}", "icon_y": "{y}"}}',
        hx_target="#desktop",
        hx_swap="beforeend"
    )
    
def Desktop():
    return Div(
        DesktopIcon("Documents", "folder", 1, 1),
        DesktopIcon("Programs", "folder", 2, 1), 
        DesktopIcon("Game of Life", "program", 1, 2),
        cls="desktop-container",
        id="desktop"
    )