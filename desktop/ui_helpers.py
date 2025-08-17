# desktop/ui_helpers.py
"""Reusable UI component builders following DRY principle."""

from fasthtml.common import Button, NotStr, Option


def create_icon(
    name: str, size: int = None, alt: str = None, cls: str = 'icon-svg'
) -> NotStr:
    """Generate icon IMG element with consistent structure."""
    alt_text = alt or name.replace('-', ' ').title()
    style = f' style="width: {size}px; height: {size}px;"' if size else ''

    return NotStr(
        f'<img src="/static/icons/{name}.svg" alt="{alt_text}" class="{cls}"{style}>'
    )


def window_control_icon(icon_type: str, size: int = 16) -> NotStr:
    """Create window control icons (minimize/maximize/close)."""
    paths = {
        'minimize': '/static/icons/window-minimize.svg',
        'maximize': '/static/icons/window-maximize.svg',
        'close': '/static/icons/window-close.svg',
        'window': '/static/icons/window.svg',
    }

    path = paths.get(icon_type, paths['window'])
    style = f'width: {size}px; height: {size}px;'

    return NotStr(
        f'<img src="{path}" alt="{icon_type}" '
        f'class="window-control-svg" style="{style}">'
    )


def window_control_button(action: str, window_id: str) -> Button:
    """Create window control buttons with consistent structure."""
    return Button(
        window_control_icon(action, 16),
        onclick=f"windowManager.{action}('{window_id}')",
        cls=f'window-{action}',
    )


def create_option(display: str, value: str, selected: bool) -> Option:
    """Generate Option element with selection state."""
    return Option(display, value=value, selected=selected)


# Theme and font configurations
THEME_COLORS = [
    ('Matrix Green', 'green'),
    ('Cyber Cyan', 'cyan'),
    ('Terminal Amber', 'amber'),
    ('Neon Purple', 'purple'),
    ('Blood Red', 'red'),
    ('Retro Orange', 'orange'),
    ('Hot Pink', 'pink'),
    ('Electric Lime', 'lime'),
    ('Neon Blue', 'blue'),
    ('Pure White', 'white'),
]

FONT_OPTIONS = [
    ('Courier New', 'courier'),
    ('Monaco', 'monaco'),
    ('Consolas', 'consolas'),
    ('Fira Code', 'fira'),
    ('Ubuntu Mono', 'ubuntu'),
    ('Source Code Pro', 'source'),
    ('JetBrains Mono', 'jetbrains'),
    ('Roboto Mono', 'roboto'),
    ('Inconsolata', 'inconsolata'),
]

# Icon mappings for desktop items
DESKTOP_ICONS = {
    'folder': 'folder',
    'eReader': 'book-open',
    'Highlights': 'highlighter',
    'Settings': 'settings',
    'Game of Life': 'gamepad',
    'default_program': 'gamepad',
}


def get_desktop_icon(name: str, item_type: str) -> NotStr:
    """Get appropriate icon for desktop item."""
    if item_type == 'folder':
        icon_name = 'folder'
    elif item_type == 'program' and name in DESKTOP_ICONS:
        icon_name = DESKTOP_ICONS[name]
    else:
        icon_name = DESKTOP_ICONS.get('default_program', 'folder')

    return create_icon(icon_name, alt=name)
