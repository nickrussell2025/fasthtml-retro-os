from fasthtml.common import *

def DesktopIcon(name: str, icon_symbol: str, item_type: str, x: int, y: int):
    """Reusable desktop icon component"""
    return Div(
        Div(icon_symbol, cls="icon-symbol"),
        Div(name, cls="icon-label"),
        cls="desktop-icon",
        style=f"position: absolute; top: {y}px; left: {x}px;",
        hx_post="/desktop/open",
        hx_vals=f'{{"item_type": "{item_type}", "item_name": "{name}"}}'
    )

def Desktop():
    """Desktop with scattered icons"""
    icons = [
        ("Documents", "📁", "folder", 50, 80),
        ("Programs", "📁", "folder", 150, 80), 
        ("Game of Life", "🎮", "program", 100, 200),
    ]
    
    return Div(
        *[DesktopIcon(name, symbol, item_type, x, y) 
          for name, symbol, item_type, x, y in icons],
        cls="desktop-container",
        id="desktop"
    )