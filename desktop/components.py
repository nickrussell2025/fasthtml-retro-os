# desktop/components.py
"""Desktop UI components for the retro OS interface."""

from functools import lru_cache

from fasthtml.common import *

from desktop.state import (
    FOLDER_CONTENTS,
    ICON_POSITIONS,
    settings_manager,
)

from .ui_helpers import (
    FONT_OPTIONS,
    THEME_COLORS,
    create_icon,
    create_option,
    get_desktop_icon,
    window_control_button,
    window_control_icon,  # This was missing!
)


def Icon(name, cls='', size=None, alt=None):
    """Clean icon generation using helper."""
    return create_icon(name, size, alt, cls)


def WindowIcon(icon_type, size=16):
    """Delegates to helper for window controls."""
    return window_control_icon(icon_type, size)


def TitleBar(title, window_id):
    """Cleaner title bar with extracted button logic."""
    return Div(
        Span(title, cls='window-title'),
        Div(
            window_control_button('minimize', window_id),
            window_control_button('maximize', window_id),
            window_control_button('close', window_id),
            cls='window-controls',
        ),
        cls='window-title-bar',
        id=f'titlebar-{window_id}',
    )


@lru_cache(maxsize=15)
def cached_window_titlebar(title: str, window_id: str):
    """Cache window titlebar generation - uses new helper functions."""
    return Div(
        Span(title, cls='window-title'),
        Div(
            window_control_button('minimize', window_id),
            window_control_button('maximize', window_id),
            window_control_button('close', window_id),
            cls='window-controls',
        ),
        cls='window-titlebar',
    )


def Window(title: str, content: FT, window_id: str = None, transparent: bool = False):
    """Reusable window component with caching"""
    if window_id is None:
        window_id = f'window-{title.replace(" ", "-").lower()}'

    # Get cached titlebar
    titlebar = cached_window_titlebar(title, window_id)

    # Build window styling
    style = 'position: absolute; left: 100px; top: 100px; z-index: 1000;'
    if transparent:
        style += ' background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(2px);'

    return Div(
        titlebar,
        Div(content, cls='window-content'),
        Div(cls='resize-handle'),
        cls='window-frame',
        id=window_id,
        style=style,
    )


def CreateContent(name, item_type):
    """Create appropriate content based on item type and name"""
    print(f"DEBUG: CreateContent called with name='{name}', item_type='{item_type}'")

    if item_type == 'folder':
        files = FOLDER_CONTENTS.get(
            name,
            [
                Div(
                    Icon('folder', 'file-icon'),
                    ' Empty folder',
                    cls='empty-folder-message',
                )
            ],
        )

        return Div(
            *[Div(file_item, cls='file-item') for file_item in files],
            cls='file-explorer',
        )

    elif item_type == 'program':
        if name == 'Game of Life':
            from programs.game_of_life.components import GameContainer
            from programs.game_of_life.game import game

            return GameContainer(game)
        elif name == 'eReader':
            from programs.ereader.ereader import EReaderProgram

            program = EReaderProgram()
            return program.get_window_content()
        elif name == 'Settings':
            return SystemSettings()
        elif name == 'Highlights':
            print('DEBUG: Matched Highlights.txt!')
            return HighlightsDisplay()
        else:
            return Div(
                H3(f'{name}'),
                P(f'This is the {name} application interface.'),
                Button('Start', cls='game-btn'),
                cls='program-content',
            )
    else:
        return Div(f'Unknown item type: {item_type}', cls='error-content')


@lru_cache(maxsize=20)
def cached_icon_content(name: str, item_type: str, is_open: bool):
    """Cache icon generation using helper function."""
    # Use the helper function instead of manual string building
    icon = get_desktop_icon(name, item_type)

    return (Div(icon, cls='icon-symbol'), Div(name, cls='icon-label'))


def DesktopIcon(name, item_type, oob_update=False):
    """Render desktop icon - always show closed folders"""
    # Get position from configuration
    if name not in ICON_POSITIONS:
        raise ValueError(f'No position defined for icon: {name}')

    x, y = ICON_POSITIONS[name]

    # Always pass False for is_open - client handles visual state
    icon_symbol, icon_label = cached_icon_content(name, item_type, False)

    # Create unique ID for this icon
    icon_id = f'icon-{name.replace(" ", "-").lower()}'

    # Build component attributes
    attrs = {
        'cls': 'desktop-icon',
        'id': icon_id,
        'style': f'grid-column: {x}; grid-row: {y};',
        'hx_post': '/open',
        'hx_vals': (
            f'{{"name": "{name}", "type": "{item_type}", "icon_x": {x}, "icon_y": {y}}}'
        ),
        'hx_target': '#desktop',
        'hx_swap': 'beforeend',
    }

    # Add OOB marker if requested
    if oob_update:
        attrs['hx_swap_oob'] = 'true'

    return Div(icon_symbol, icon_label, **attrs)


def Desktop():
    """Create the main desktop layout with icons"""
    print(f'🔍 DEBUG: Available icons: {list(ICON_POSITIONS.keys())}')

    return Div(
        # Generate desktop icons from position registry
        *[
            DesktopIcon(
                name, 'folder' if name in ['Documents', 'Programs'] else 'program'
            )
            for name in ICON_POSITIONS.keys()
        ],
        cls='desktop-container',
        id='desktop',
    )


def SystemSettings():
    """System settings panel using helper functions."""
    current = settings_manager.get_all()

    return Div(
        H3(
            Icon('settings', 'inline-icon'),
            ' System Settings',
            style='margin-bottom: 20px; color: var(--primary-color);',
        ),
        # Theme Color Selection - using helper
        Div(
            Label('Theme Color'),
            Select(
                *[
                    create_option(name, val, current['theme_color'] == val)
                    for name, val in THEME_COLORS
                ],
                name='theme_color',
                onchange="settingsManager.save('theme_color', this.value)",
            ),
            cls='setting-group',
        ),
        # Font Selection - using helper
        Div(
            Label('System Font'),
            Select(
                *[
                    create_option(name, val, current['font'] == val)
                    for name, val in FONT_OPTIONS
                ],
                name='font',
                onchange="settingsManager.save('font', this.value)",
            ),
            cls='setting-group',
        ),
        # Scanline Intensity
        Div(
            Label('Scanline Effect'),
            Input(
                type='range',
                min='0',
                max='0.3',
                step='0.01',
                value=str(current['scanline_intensity']),
                oninput=(
                    "settingsManager.save('scanline_intensity', parseFloat(this.value))"
                ),
            ),
            Div(
                f'Current: {current["scanline_intensity"]:.2f}',
                style=('font-size: 11px; color: var(--primary-dim); margin-top: 4px;'),
            ),
            cls='setting-group',
        ),
        cls='settings-content',
        style='padding: 20px; color: var(--primary-color);',
    )


def HighlightsDisplay():
    """Basic highlights viewer structure"""
    return Div(
        H3('Your Highlights'),
        Div(id='highlights-list', cls='highlights-content'),
        cls='highlights-viewer',
    )
