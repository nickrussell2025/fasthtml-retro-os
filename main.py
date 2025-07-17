from fasthtml.common import (
    Button,
    Div,
    FastHTML,
    FileResponse,
    Link,
    Script,
    Span,
    serve,
)

from desktop.components import CreateContent, Desktop, UpdatedIcon, Window, wm

# Application setup with static file serving
js_script = Script(src='/static/js/desktop.js')
app = FastHTML(hdrs=(Link(rel='stylesheet', href='/static/css/style.css'), js_script))


@app.get('/{fname:path}.{ext:static}')
def static_file(fname: str, ext: str):
    """Serve static files (CSS, JS, images)"""
    return FileResponse(f'{fname}.{ext}')


@app.get('/')
def home():
    """Main desktop view"""
    return Desktop()


@app.post('/open')
def open_item(name: str, type: str, icon_x: int, icon_y: int):
    """Handle icon click to open window with icon state update"""
    print(f'DEBUG: Opening {name}, type: {type}, position: ({icon_x}, {icon_y})')

    try:
        # Create content based on item type
        content = CreateContent(name, type)
        print('DEBUG: Content created successfully')

        # Create window through WindowManager
        window_data = wm.create_window(name, content, icon_x, icon_y)

        if window_data is None:
            print(f'DEBUG: Window already exists for {name}')
            return ''  # Window already exists, don't create duplicate

        print(f'DEBUG: Window data created: {window_data["id"]}')

        # Create the window
        window = Window(window_data)

        # If this is a folder, also return an updated icon
        if type == 'folder':
            updated_icon = UpdatedIcon(name, type, icon_x, icon_y)
            # Return both the window and the updated icon
            return window, updated_icon
        else:
            # For programs, just return the window
            return window

    except Exception as e:
        print(f'ERROR in open_item: {e}')
        import traceback

        traceback.print_exc()
        return Div(f'Error opening {name}: {str(e)}', cls='error-message')


@app.post('/window/{window_id}/minimize')
def minimize_window(window_id: str):
    """Minimize window to taskbar"""
    try:
        position = wm.minimize_window(window_id)
        if position is None:
            return ''

        window_data = wm.get_window(window_id)
        if not window_data:
            return ''

        # Calculate taskbar position
        bottom = 40 + (position * 30)

        return Div(
            Div(
                Span('■', cls='minimized-icon'),
                Span(window_data['name'], cls='minimized-title'),
                Button(
                    '^',
                    cls='restore-button',
                    hx_post=f'/window/{window_id}/restore',
                    hx_target=f'#{window_id}',
                    hx_swap='outerHTML',
                ),
                cls='minimized-window',
            ),
            id=window_id,
            cls='minimized-container',
            style=f'position: absolute; left: 20px; bottom: {bottom}px; z-index: 50;',
        )
    except Exception as e:
        print(f'ERROR in minimize_window: {e}')
        return ''


@app.post('/window/{window_id}/maximize')
def maximize_window(window_id: str):
    """Maximize window to full screen"""
    try:
        window_data = wm.maximize_window(window_id)
        if window_data:
            return Window(window_data, maximized=True)
        return ''
    except Exception as e:
        print(f'ERROR in maximize_window: {e}')
        return ''


@app.post('/window/{window_id}/restore')
def restore_window(window_id: str):
    """Restore window from minimized or maximized state"""
    try:
        window_data = wm.restore_window(window_id)
        if window_data:
            return Window(window_data)
        return ''
    except Exception as e:
        print(f'ERROR in restore_window: {e}')
        return ''


@app.delete('/window/{window_id}')
def close_window(window_id: str):
    """Close window and clean up state with icon update"""
    try:
        print(f'DEBUG: Closing window {window_id}')

        # Clean up window state (this also closes folder if applicable)
        closed_window_data = wm.close_window(window_id)

        # If this was a folder window, return an updated icon
        if closed_window_data and closed_window_data.get('item_type') == 'folder':
            icon_positions = {'Documents': (1, 1), 'Programs': (2, 1)}

            name = closed_window_data['name']
            if name in icon_positions:
                x, y = icon_positions[name]
                updated_icon = UpdatedIcon(name, 'folder', x, y)
                return updated_icon

        # For non-folder windows or if no position found, just return empty
        return ''

    except Exception as e:
        print(f'ERROR in close_window: {e}')
        return ''


@app.post('/window/{window_id}/move')
def move_window(window_id: str, x: int, y: int):
    """Update window position (called by JavaScript drag handler)"""
    try:
        wm.update_window_position(window_id, x, y)
        return ''  # Just acknowledge, no UI update needed
    except Exception as e:
        print(f'ERROR in move_window: {e}')
        return ''


@app.get('/refresh-desktop')
def refresh_desktop():
    """Return updated desktop (for debugging purposes)"""
    return Desktop()


if __name__ == '__main__':
    serve()
