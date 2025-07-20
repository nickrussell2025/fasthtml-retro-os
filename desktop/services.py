"""
Desktop Services - Incremental Migration
Start by wrapping existing logic without changing it
"""
from fasthtml.common import Style
from desktop.state import ICON_POSITIONS, SYSTEM_FONTS, window_manager, settings_manager
from desktop.components import CreateContent, DesktopIcon, Window, WindowIcon

from desktop.components import CreateContent, DesktopIcon, Window
from desktop.state import window_manager

class DesktopService:
    def __init__(self):
        self.window_manager = window_manager

    def open_item(self, name: str, type: str, icon_x: int, icon_y: int):
        """Create window content only"""
        content = CreateContent(name, type)
        window_data = self.window_manager.create_window(name, content, icon_x, icon_y)

        if window_data is None:
            return None, None

        window = Window(window_data)

        if type == "folder":
            updated_icon = DesktopIcon(name, type, oob_update=True)
            return window, updated_icon
        return window, None

    def close_window(self, window_id: str):
        """Clean up server data only"""
        closed_window_data = self.window_manager.close_window(window_id)
        
        if (closed_window_data and 
            closed_window_data.get('item_type') == 'folder'):
            return DesktopIcon(closed_window_data['name'], 'folder', oob_update=True)
        return None

# Global instance
desktop_service = DesktopService()


# def get_window_icon_html(icon_type="window", size=16):
#     """Generate HTML string for window icons - efficient for f-string usage"""
#     icon_paths = {
#         "window": "/static/icons/folder.svg",
#         "restore": "/static/icons/circle-chevron-up.svg"
#     }
#     icon_path = icon_paths.get(icon_type, icon_paths["window"])
#     return f'<img src="{icon_path}" alt="{icon_type}" class="window-control-svg" style="width: {size}px; height: {size}px;">'


# class DesktopService:
#     def __init__(self):
#         self.window_manager = window_manager

#     def open_item(self, name: str, type: str, icon_x: int, icon_y: int):
#         """Wrapper around existing open logic - no changes yet"""
#         # Copy exact logic from main.py open_item
#         content = CreateContent(name, type)
#         window_data = self.window_manager.create_window(name, content, icon_x, icon_y)

#         if window_data is None:
#             print(f"Window {name} already exists - ignoring click")
#             return None, None

#         window = Window(window_data)

#         if type == "folder":
#             updated_icon = DesktopIcon(name, type, oob_update=True)
#             return window, updated_icon

#         return window, None

#     def restore_window(self, window_id: str):
#         """Move restore logic to service layer"""
#         window_data = self.window_manager.restore_window(window_id)

#         if not window_data:
#             return None

#         return Window(window_data)

#     def maximize_window(self, window_id: str):
#         """Move maximize logic to service layer"""
#         window_data = self.window_manager.maximize_window(window_id)

#         if not window_data:
#             return None

#         return Window(window_data, maximized=True)

#     def close_window(self, window_id: str):
#         """Move close logic to service layer"""
#         # Clean up window state
#         closed_window_data = self.window_manager.close_window(window_id)

#         # If folder was closed, return updated icon via OOB
#         if (closed_window_data and
#             closed_window_data.get('item_type') == 'folder' and
#             closed_window_data['name'] in ICON_POSITIONS):

#             return DesktopIcon(closed_window_data['name'], 'folder', oob_update=True)

#         return None

#     def move_window(self, window_id: str, x: int, y: int):
#         """Move window position logic to service layer"""
#         success = self.window_manager.update_window_position(window_id, x, y)
#         return success

#     def update_theme(self, theme_color: str):
#         hue_map = {"green": 120, "cyan": 180, "amber": 45, "purple": 270}
#         hue = hue_map[theme_color]

#         return Style(f"""
#             :root {{ --primary-hue: {hue} !important; }}
#         """)

#     def update_font(self, font: str):
#         font_family = SYSTEM_FONTS[font]
#         return Style(f"""
#             :root {{ --system-font: {font_family} !important; }}
#         """)

#     def update_scanlines(self, scanline_intensity: float):
#         return Style(f"""
#             :root {{ --scanline-opacity: {scanline_intensity} !important; }}
#         """)

#     def update_theme(self, theme_color: str):
#         settings_manager.update_setting('theme_color', theme_color)
#         hue_map = {"green": 120, "cyan": 180, "amber": 45, "purple": 270}
#         hue = hue_map[theme_color]
        
#         return Style(f"""
#             :root {{ --primary-hue: {hue} !important; }}
#         """)

#     def update_font(self, font: str):
#         settings_manager.update_setting('font', font)
#         font_family = SYSTEM_FONTS[font]
#         return Style(f"""
#             :root {{ --system-font: {font_family} !important; }}
#         """)

#     def update_scanlines(self, scanline_intensity: float):
#         settings_manager.update_setting('scanline_intensity', scanline_intensity)
#         return Style(f"""
#             :root {{ --scanline-opacity: {scanline_intensity} !important; }}
#         """)
        
# # Global instance
# desktop_service = DesktopService()
