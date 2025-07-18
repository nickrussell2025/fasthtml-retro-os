"""
Desktop UI Components
Pure rendering functions - no state management
"""
from fasthtml.common import *

from desktop.state import FOLDER_CONTENTS, ICON_POSITIONS, window_manager


def Window(window_data, maximized=False):
    """Render window from standardized window data structure"""
    if not window_data:
        return Div("Error: No window data provided")

    # Determine window styling based on state
    if maximized or window_data.get('maximized', False):
        style = "position: absolute; left: 0; top: 0; width: 100vw; height: 100vh;"
    else:
        x, y = window_data['position']
        z = window_data['z_index']
        style = f"position: absolute; left: {x}px; top: {y}px; z-index: {z};"

    window_id = window_data['id']

    return Div(
        # Window titlebar with controls
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
        # Window content area
        Div(window_data['content'], cls="window-content"),
        Div(cls="resize-handle"),
        cls="window-frame",
        id=window_id,
        style=style
    )

def CreateContent(name, item_type):
    """Create appropriate content based on item type and name"""
    if item_type == "folder":
        files = FOLDER_CONTENTS.get(name, ["📂 Empty folder"])

        return Div(
            *[Div(file_item, cls="file-item") for file_item in files],
            cls="file-explorer"
        )

    elif item_type == "program":
        if name == "Game of Life":
            return Div(
                H3("Conway's Game of Life"),
                Div("🟩🟩⬜⬜🟩", cls="game-preview"),
                Div(
                    Button("▶️ Play", cls="game-btn"),
                    Button("⏸️ Pause", cls="game-btn"),
                    Button("🔄 Reset", cls="game-btn"),
                    cls="game-controls"
                ),
                P("Click cells to toggle. Watch patterns evolve!"),
                cls="game-interface"
            )
        else:
            return Div(
                H3(f"{name}"),
                P(f"This is the {name} application interface."),
                Button("Start", cls="game-btn"),
                cls="program-content"
            )
    else:
        return Div(f"Unknown item type: {item_type}", cls="error-content")

def DesktopIcon(name, item_type, oob_update=False):
    """
    Render desktop icon based on current state
    Args:
        name: Icon name
        item_type: 'folder' or 'program'
        oob_update: If True, marks for out-of-band HTMX update
    """
    # Get position from configuration
    if name not in ICON_POSITIONS:
        raise ValueError(f"No position defined for icon: {name}")

    x, y = ICON_POSITIONS[name]

    # Determine icon based on type and current state
    if item_type == "folder" and window_manager.is_folder_open(name):
        icon = "🗁"  # Open folder
    elif item_type == "folder":
        icon = "🗀"  # Closed folder
    elif item_type == "program":
        icon = "⚏"   # Program icon
    else:
        icon = "🗎"   # Default file icon

    # Create unique ID for this icon
    icon_id = f"icon-{name.replace(' ', '-').lower()}"

    # Build component attributes
    attrs = {
        'cls': "desktop-icon",
        'id': icon_id,
        'style': f"grid-column: {x}; grid-row: {y};",
        'hx_post': "/open",
        'hx_vals': (
            f'{{"name": "{name}", "type": "{item_type}", '
            f'"icon_x": {x}, "icon_y": {y}}}'
        ),
        'hx_target': "#desktop",
        'hx_swap': "beforeend"
    }

    # Add OOB marker if requested
    if oob_update:
        attrs['hx_swap_oob'] = 'true'

    return Div(
        Div(icon, cls="icon-symbol"),
        Div(name, cls="icon-label"),
        **attrs
    )

def Desktop():
    """Create the main desktop layout with icons"""
    return Div(
        # Generate desktop icons from position registry
        *[DesktopIcon(name, "folder" if name in ["Documents", "Programs"] else "program")
          for name in ICON_POSITIONS.keys()],
        cls="desktop-container",
        id="desktop"
    )