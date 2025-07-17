from fasthtml.common import *


class WindowManager:
    def __init__(self):
        self.windows = {}
        self.minimized_positions = {}
        self.available_positions = set(range(10))
        self.next_z_index = 100
        self.open_folders = set()

    def create_window(self, name, content, icon_x, icon_y):
        """Creates a window and returns the complete window data structure"""
        window_id = f'win-{name.replace(" ", "-").lower()}'

        # Check if window already exists
        if window_id in self.windows:
            return None  # Signal that window already exists

        # Calculate position based on icon location
        x = (icon_x * 120) + 150
        y = (icon_y * 120) + 50

        # Create window data structure
        window_data = {
            'id': window_id,
            'name': name,
            'content': content,
            'position': (x, y),
            'z_index': self.next_z_index,
            'maximized': False,
            'item_type': 'folder' if name in ['Documents', 'Programs'] else 'program',
        }

        # Store in windows registry
        self.windows[window_id] = window_data
        self.next_z_index += 1

        # Track folder state if this is a folder
        if window_data['item_type'] == 'folder':
            self.open_folders.add(name)

        return window_data

    def get_window(self, window_id):
        """Get window data by ID"""
        return self.windows.get(window_id)

    def minimize_window(self, window_id):
        """Minimize window and return position in taskbar"""
        if window_id not in self.windows or not self.available_positions:
            return 0
        position = min(self.available_positions)
        self.available_positions.remove(position)
        self.minimized_positions[window_id] = position
        return position

    def restore_window(self, window_id):
        """Restore minimized window"""
        if window_id in self.minimized_positions:
            pos = self.minimized_positions.pop(window_id)
            self.available_positions.add(pos)
        if window_id in self.windows:
            self.windows[window_id]['maximized'] = False
        return self.windows.get(window_id)

    def maximize_window(self, window_id):
        """Maximize window"""
        if window_id in self.windows:
            self.windows[window_id]['maximized'] = True
        return self.windows.get(window_id)

    def close_window(self, window_id):
        """Close window and clean up state"""
        # Clean up minimized position if exists
        if window_id in self.minimized_positions:
            pos = self.minimized_positions.pop(window_id)
            self.available_positions.add(pos)

        # Get window data before deletion for cleanup
        window_data = self.windows.get(window_id)
        if window_data and window_data.get('item_type') == 'folder':
            # Close folder state
            self.close_folder(window_data['name'])

        # Remove from windows registry
        self.windows.pop(window_id, None)

        return window_data  # Return data for potential icon updates

    def update_window_position(self, window_id, x, y):
        """Update window position (for dragging)"""
        if window_id in self.windows:
            self.windows[window_id]['position'] = (x, y)

    def open_folder(self, name):
        """Mark folder as open"""
        self.open_folders.add(name)

    def close_folder(self, name):
        """Mark folder as closed"""
        self.open_folders.discard(name)

    def is_folder_open(self, name):
        """Check if folder is currently open"""
        return name in self.open_folders


# Global window manager instance
wm = WindowManager()


def Window(window_data, maximized=False):
    """Render window from standardized window data structure"""
    if not window_data:
        return Div('Error: No window data provided')

    # Determine window styling based on state
    if maximized or window_data.get('maximized', False):
        style = 'position: absolute; left: 0; top: 0; width: 100vw; height: 100vh;'
    else:
        x, y = window_data['position']
        z = window_data['z_index']
        style = f'position: absolute; left: {x}px; top: {y}px; z-index: {z};'

    window_id = window_data['id']

    return Div(
        # Window titlebar with controls
        Div(
            Span(window_data['name'], cls='window-title'),
            Div(
                Button(
                    '▼',
                    cls='window-minimize',
                    hx_post=f'/window/{window_id}/minimize',
                    hx_target=f'#{window_id}',
                    hx_swap='outerHTML',
                ),
                Button(
                    '▲',
                    cls='window-maximize',
                    hx_post=f'/window/{window_id}/maximize',
                    hx_target=f'#{window_id}',
                    hx_swap='outerHTML',
                ),
                Button(
                    '■',
                    cls='window-close',
                    hx_delete=f'/window/{window_id}',
                    hx_target=f'#{window_id}',
                    hx_swap='outerHTML',
                ),
                cls='window-controls',
            ),
            cls='window-titlebar',
        ),
        # Window content area
        Div(window_data['content'], cls='window-content'),
        cls='window-frame',
        id=window_id,
        style=style,
    )


def CreateContent(name, item_type):
    """Create appropriate content based on item type and name"""
    if item_type == 'folder':
        # Define folder contents
        folder_contents = {
            'Documents': ['📄 resume.txt', '📄 notes.txt', '📁 projects/'],
            'Programs': ['🎮 Game of Life', '🧮 Calculator', '📝 Text Editor'],
        }

        files = folder_contents.get(name, ['📂 Empty folder'])

        return Div(
            *[Div(file_item, cls='file-item') for file_item in files],
            cls='file-explorer',
        )

    elif item_type == 'program':
        if name == 'Game of Life':
            return Div(
                H3("Conway's Game of Life"),
                Div('🟩🟩⬜⬜🟩', cls='game-preview'),
                Div(
                    Button('▶️ Play', cls='game-btn'),
                    Button('⏸️ Pause', cls='game-btn'),
                    Button('🔄 Reset', cls='game-btn'),
                    cls='game-controls',
                ),
                P('Click cells to toggle. Watch patterns evolve!'),
                cls='game-interface',
            )
        else:
            return Div(
                H3(f'{name}'),
                P(f'This is the {name} application interface.'),
                Button('Start', cls='game-btn'),
                cls='program-content',
            )
    else:
        return Div(f'Unknown item type: {item_type}', cls='error-content')


def DesktopIcon(name, item_type, x, y):
    """Create desktop icon with proper state management"""
    # Determine icon based on type and state
    if item_type == 'folder' and wm.is_folder_open(name):
        icon = '🗁'  # Open folder
    elif item_type == 'folder':
        icon = '🗀'  # Closed folder
    elif item_type == 'program':
        icon = '⚏'  # Program icon
    else:
        icon = '🗎'  # Default file icon

    # Create unique ID for this icon for out-of-band updates
    icon_id = f'icon-{name.replace(" ", "-").lower()}'

    return Div(
        Div(icon, cls='icon-symbol'),
        Div(name, cls='icon-label'),
        cls='desktop-icon',
        id=icon_id,  # Add ID for targeting updates
        style=f'grid-column: {x}; grid-row: {y};',
        hx_post='/open',
        hx_vals=(
            f'{{"name": "{name}", "type": "{item_type}", "icon_x": {x}, "icon_y": {y}}}'
        ),
        hx_target='#desktop',
        hx_swap='beforeend',
    )


def UpdatedIcon(name, item_type, x, y):
    """Create an updated icon for out-of-band swapping"""
    # This is the same as DesktopIcon but marked for OOB update
    icon_id = f'icon-{name.replace(" ", "-").lower()}'

    # Determine current icon state
    if item_type == 'folder' and wm.is_folder_open(name):
        icon = '🗁'  # Open folder
    elif item_type == 'folder':
        icon = '🗀'  # Closed folder
    elif item_type == 'program':
        icon = '⚏'  # Program icon
    else:
        icon = '🗎'  # Default file icon

    return Div(
        Div(icon, cls='icon-symbol'),
        Div(name, cls='icon-label'),
        cls='desktop-icon',
        id=icon_id,
        style=f'grid-column: {x}; grid-row: {y};',
        hx_post='/open',
        hx_vals=(
            f'{{"name": "{name}", "type": "{item_type}", "icon_x": {x}, "icon_y": {y}}}'
        ),
        hx_target='#desktop',
        hx_swap='beforeend',
        hx_swap_oob='true',  # This tells HTMX to update this element out-of-band
    )


def Desktop():
    """Create the main desktop layout with icons"""
    return Div(
        # Desktop icons positioned on grid
        DesktopIcon('Documents', 'folder', 1, 1),
        DesktopIcon('Programs', 'folder', 2, 1),
        DesktopIcon('Game of Life', 'program', 1, 2),
        cls='desktop-container',
        id='desktop',
    )
