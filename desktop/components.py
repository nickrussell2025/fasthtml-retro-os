from fasthtml.common import *
from desktop.state import FOLDER_CONTENTS, ICON_POSITIONS, window_manager, settings_manager
from functools import lru_cache


def Icon(name: str, cls: str = "icon-svg", alt: str = None, size: int = None):
    """Reusable SVG icon component with theming support"""
    if alt is None:
        alt = name.title().replace('-', ' ')
    
    style = ""
    if size:
        style = f' style="width: {size}px; height: {size}px;"'
    
    return NotStr(f'<img src="/static/icons/{name}.svg" alt="{alt}" class="{cls}"{style}>')


def WindowIcon(icon_type: str, size: int = 16):
    """Create SVG icons for window controls and taskbar using existing icon files"""
    icon_paths = {
        'minimize': '/static/icons/circle-chevron-down.svg',
        'maximize': '/static/icons/circle-chevron-up.svg', 
        'close': '/static/icons/circle-x.svg',
        'restore': '/static/icons/circle-chevron-up.svg',
        'window': '/static/icons/folder.svg'
    }
    
    icon_path = icon_paths.get(icon_type, icon_paths['window'])
    
    return NotStr(f'<img src="{icon_path}" alt="{icon_type}" class="window-control-svg" style="width: {size}px; height: {size}px;">')


@lru_cache(maxsize=15)
def cached_window_titlebar(title: str, window_id: str):
    """Cache window titlebar generation"""
    return Div(
        Span(title, cls="window-title"),
        Div(
            Button(WindowIcon("minimize", 16), onclick=f"windowManager.minimize('{window_id}')", cls="window-minimize"),
            Button(WindowIcon("maximize", 16), onclick=f"windowManager.maximize('{window_id}')", cls="window-maximize"),  
            Button(WindowIcon("close", 16), onclick=f"windowManager.close('{window_id}')", cls="window-close"),
            cls="window-controls"
        ),
        cls="window-titlebar"
    )


def Window(title: str, content: FT, window_id: str = None, transparent: bool = False):
    """Reusable window component with caching"""
    if window_id is None:
        window_id = f"window-{title.replace(' ', '-').lower()}"
    
    # Get cached titlebar
    titlebar = cached_window_titlebar(title, window_id)
    
    # Build window styling
    style = "position: absolute; left: 100px; top: 100px; z-index: 1000;"
    if transparent:
        style += " background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(2px);"
    
    return Div(
        titlebar,
        Div(content, cls="window-content"),
        Div(cls="resize-handle"),
        cls="window-frame",
        id=window_id,
        style=style
    )


def CreateContent(name, item_type):
    """Create appropriate content based on item type and name"""
    print(f"DEBUG: CreateContent called with name='{name}', item_type='{item_type}'")

    if item_type == "folder":
        files = FOLDER_CONTENTS.get(name, [Div(Icon("folder", "file-icon"), " Empty folder", cls="empty-folder-message")
        ])

        return Div(
            *[Div(file_item, cls="file-item") for file_item in files],
            cls="file-explorer"
        )

    elif item_type == "program":
        if name == "Game of Life":
            from programs.game_of_life.components import GameContainer
            from programs.game_of_life.game import game
            return GameContainer(game)
        elif name == "eReader":
            from programs.ereader.ereader import EReaderProgram
            program = EReaderProgram()
            return program.get_window_content()
        elif name == "Settings":
            return SystemSettings()
        elif name == "Highlights":
            print("DEBUG: Matched Highlights.txt!")
            return HighlightsDisplay()
        else:
            return Div(
                H3(f"{name}"),
                P(f"This is the {name} application interface."),
                Button("Start", cls="game-btn"),
                cls="program-content"
            )
    else:
        return Div(f"Unknown item type: {item_type}", cls="error-content")


@lru_cache(maxsize=20)
def cached_icon_content(name: str, item_type: str, is_open: bool):
    """Cache icon SVG generation - ignore is_open, always show closed folders"""
    # Always show closed folder - client handles open state
    if item_type == "folder":
        icon = NotStr('<img src="/static/icons/folder.svg" alt="Folder" class="icon-svg">')
    elif item_type == "program" and name == "eReader":
        icon = NotStr('<img src="/static/icons/book-open.svg" alt="eReader" class="icon-svg">')
    elif item_type == "program" and name == "Highlights":
        icon = NotStr('<img src="/static/icons/highlighter.svg" alt="Highlights" class="icon-svg">')
    elif item_type == "program" and name == "Settings":
        icon = NotStr('<img src="/static/icons/settings.svg" alt="Settings" class="icon-svg">')
    elif item_type == "program" and name == "Game of Life":
        icon = NotStr('<img src="/static/icons/gamepad.svg" alt="Game of Life" class="icon-svg">')
    elif item_type == "program":
        icon = NotStr('<img src="/static/icons/gamepad.svg" alt="Program" class="icon-svg">')
    else:
        icon = NotStr('<img src="/static/icons/folder.svg" alt="File" class="icon-svg">')
    
    return (
        Div(icon, cls="icon-symbol"),
        Div(name, cls="icon-label")
    )

def DesktopIcon(name, item_type, oob_update=False):
    """Render desktop icon - always show closed folders"""
    # Get position from configuration
    if name not in ICON_POSITIONS:
        raise ValueError(f"No position defined for icon: {name}")

    x, y = ICON_POSITIONS[name]
    
    # Always pass False for is_open - client handles visual state
    icon_symbol, icon_label = cached_icon_content(name, item_type, False)

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
        icon_symbol,
        icon_label,
        **attrs
    )


def Desktop():
    """Create the main desktop layout with icons"""
    print(f"🔍 DEBUG: Available icons: {list(ICON_POSITIONS.keys())}")

    return Div(
        # Generate desktop icons from position registry
        *[DesktopIcon(name, "folder" if name in ["Documents", "Programs"] else "program")
          for name in ICON_POSITIONS.keys()],
        cls="desktop-container",
        id="desktop"
    )


def SystemSettings():
    """System settings panel that applies changes immediately via JavaScript"""
    
    # Import your settings manager here 
    from desktop.state import settings_manager
    current = settings_manager.get_all()
    
    return Div(
        H3(Icon("settings", "inline-icon"), " System Settings", style="margin-bottom: 20px; color: var(--primary-color);"),
        
        # Theme Color Selection - immediate JavaScript updates
        Div(
            Label("Theme Color"),
            Select(
                Option("Matrix Green", value="green", selected=current['theme_color'] == 'green'),
                Option("Cyber Cyan", value="cyan", selected=current['theme_color'] == 'cyan'),
                Option("Terminal Amber", value="amber", selected=current['theme_color'] == 'amber'), 
                Option("Neon Purple", value="purple", selected=current['theme_color'] == 'purple'),
                Option("Blood Red", value="red", selected=current['theme_color'] == 'red'),
                Option("Retro Orange", value="orange", selected=current['theme_color'] == 'orange'),
                Option("Hot Pink", value="pink", selected=current['theme_color'] == 'pink'),
                Option("Electric Lime", value="lime", selected=current['theme_color'] == 'lime'),
                Option("Neon Blue", value="blue", selected=current['theme_color'] == 'blue'),
                Option("Pure White", value="white", selected=current['theme_color'] == 'white'),
                name="theme_color",
                onchange="settingsManager.save('theme_color', this.value)"  # Immediate JavaScript call
            ),
            cls="setting-group"
        ),
        
        # Font Selection - immediate JavaScript updates
        Div(
            Label("System Font"),
            Select(
                Option("Courier New", value="courier", selected=current['font'] == 'courier'),
                Option("Monaco", value="monaco", selected=current['font'] == 'monaco'),
                Option("Consolas", value="consolas", selected=current['font'] == 'consolas'),
                Option("Fira Code", value="fira", selected=current['font'] == 'fira'),
                Option("Ubuntu Mono", value="ubuntu", selected=current['font'] == 'ubuntu'),
                Option("Source Code Pro", value="source", selected=current['font'] == 'source'),
                Option("JetBrains Mono", value="jetbrains", selected=current['font'] == 'jetbrains'),
                Option("Roboto Mono", value="roboto", selected=current['font'] == 'roboto'),
                Option("Inconsolata", value="inconsolata", selected=current['font'] == 'inconsolata'),
                name="font",
                onchange="settingsManager.save('font', this.value)"  # Immediate JavaScript call
            ),
            cls="setting-group"
        ),
        
        # Scanline Intensity - immediate JavaScript updates
        Div(
            Label("Scanline Effect"),
            Input(
                type="range",
                min="0",
                max="0.3",
                step="0.01",
                value=str(current['scanline_intensity']),
                oninput="settingsManager.save('scanline_intensity', parseFloat(this.value))"  # Immediate update
            ),
            Div(f"Current: {current['scanline_intensity']:.2f}", 
                style="font-size: 11px; color: var(--primary-dim); margin-top: 4px;"),
            cls="setting-group"
        ),
        
        cls="settings-content",
        style="padding: 20px; color: var(--primary-color);"
    )


def HighlightsDisplay():
    """Basic highlights viewer structure"""
    return Div(
        H3("Your Highlights"),
        Div(id="highlights-list", cls="highlights-content"),
        cls="highlights-viewer"
    )