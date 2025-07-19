"""
Desktop State Management
Handles all window lifecycle, positioning, and folder state
"""

# Configuration constants
ICON_POSITIONS = {
    'Documents': (1, 1),
    'Programs': (2, 1),
    'Game of Life': (1, 2),
    'Settings': (3, 3),
}

FOLDER_CONTENTS = {
    "Documents": [
        "📄 resume.txt", "📄 notes.txt", "📁 projects/",
        "📄 report.docx", "📄 invoice.pdf", "📄 contract.txt",
        "📁 photos/", "📁 backups/", "📄 todo.md",
        "📄 budget.xlsx", "📄 letter.doc", "📁 archive/",
        "📄 presentation.pptx", "📄 manual.pdf"
    ],
    "Programs": ["🎮 Game of Life", "🧮 Calculator", "📝 Text Editor"]
}

THEME_COLORS = {
    "green": {
        "primary": "#00ff41",
        "primary_dim": "#00ff4155",
        "primary_glow": "#00ff4108",
        "primary_dark": "#008822"
    },
    "cyan": {
        "primary": "#00ffff",
        "primary_dim": "#00ffff55",
        "primary_glow": "#00ffff08",
        "primary_dark": "#008888"
    },
    "amber": {
        "primary": "#ffbf00",
        "primary_dim": "#ffbf0055",
        "primary_glow": "#ffbf0008",
        "primary_dark": "#cc8800"
    },
    "purple": {
        "primary": "#8a2be2",
        "primary_dim": "#8a2be255",
        "primary_glow": "#8a2be208",
        "primary_dark": "#5a1b92"
    }
}

SYSTEM_FONTS = {
    "courier": "'Courier New', monospace",
    "monaco": "'Monaco', monospace",
    "consolas": "'Consolas', monospace"
}


# Window positioning configuration
WINDOW_CONFIG = {
    'ICON_GRID_SIZE': 120,      # Pixels between icon grid positions
    'WINDOW_OFFSET_X': 150,     # Horizontal offset from icon to window
    'WINDOW_OFFSET_Y': 50,      # Vertical offset from icon to window
    'INITIAL_Z_INDEX': 100,     # Starting z-index for windows
    'MAX_MINIMIZED': 10,        # Maximum minimized windows in taskbar
}

# Taskbar configuration
TASKBAR_CONFIG = {
    'BOTTOM_MARGIN': 40,        # Distance from bottom of screen
    'ITEM_HEIGHT': 30,          # Height of each minimized window
    'LEFT_MARGIN': 20,          # Distance from left edge
}

class WindowManager:
    """Central state manager for all desktop windows"""

    def __init__(self):
        self.windows = {}
        self.minimized_positions = {}
        self.available_positions = set(range(WINDOW_CONFIG['MAX_MINIMIZED']))
        self.next_z_index = WINDOW_CONFIG['INITIAL_Z_INDEX']
        self.open_folders = set()
        self._reset_desktop()


    def create_window(self, name, content, icon_x, icon_y):
        """Creates a window and returns the complete window data structure"""
        window_id = f"win-{name.replace(' ', '-').lower()}"

        # Check if window already exists
        if window_id in self.windows:
            return None

        # Calculate position based on icon location using configuration
        x = (icon_x * WINDOW_CONFIG['ICON_GRID_SIZE']) + WINDOW_CONFIG['WINDOW_OFFSET_X']
        y = (icon_y * WINDOW_CONFIG['ICON_GRID_SIZE']) + WINDOW_CONFIG['WINDOW_OFFSET_Y']

        # Create window data structure
        window_data = {
            'id': window_id,
            'name': name,
            'content': content,
            'position': (x, y),
            'z_index': self.next_z_index,
            'maximized': False,
            'item_type': 'folder' if name in ['Documents', 'Programs'] else 'program'
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
            return None
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

        # Get window data before deletion
        window_data = self.windows.get(window_id)
        if window_data and window_data.get('item_type') == 'folder':
            self.close_folder(window_data['name'])

        # Remove from windows registry
        self.windows.pop(window_id, None)
        return window_data

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

    def calculate_taskbar_position(self, position):
        """Calculate taskbar position for minimized window"""
        return (
            TASKBAR_CONFIG['LEFT_MARGIN'],
            TASKBAR_CONFIG['BOTTOM_MARGIN'] + (position * TASKBAR_CONFIG['ITEM_HEIGHT'])
        )

    def _reset_desktop(self):
        """Reset all desktop state on startup"""
        self.windows.clear()
        self.minimized_positions.clear()
        self.available_positions = set(range(WINDOW_CONFIG['MAX_MINIMIZED']))
        self.next_z_index = WINDOW_CONFIG['INITIAL_Z_INDEX']
        self.open_folders.clear()
        print("Desktop state reset - all windows closed")

# Global state instance
window_manager = WindowManager()
