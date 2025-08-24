"""
Desktop Services - Incremental Migration
Start by wrapping existing logic without changing it
"""

from desktop.components import CreateContent, DesktopIcon, Window
from desktop.state import window_manager


class DesktopService:
    def __init__(self):
        self.window_manager = window_manager

    def open_item(self, name: str, type: str, icon_x: int, icon_y: int):
        """Create window content only"""
        print('🔍 DEBUG desktop_service.open_item: About to call CreateContent')

        content = CreateContent(name, type)
        window_data = self.window_manager.create_window(name, content, icon_x, icon_y)

        if window_data is None:
            return None, None

        window = Window(window_data['name'], content)

        if type == 'folder':
            updated_icon = DesktopIcon(name, type, oob_update=True)
            return window, updated_icon
        return window, None

    def close_window(self, window_id: str):
        """Clean up server data only"""
        closed_window_data = self.window_manager.close_window(window_id)

        if closed_window_data and closed_window_data.get('item_type') == 'folder':
            # The folder state is now closed, return updated icon
            return DesktopIcon(closed_window_data['name'], 'folder', oob_update=True)
        return None


# Global instance
desktop_service = DesktopService()
