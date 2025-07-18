"""
Desktop Services - Incremental Migration
Start by wrapping existing logic without changing it
"""
from desktop.components import CreateContent, Window, DesktopIcon
from desktop.state import window_manager, ICON_POSITIONS


class DesktopService:
    def __init__(self):
        self.window_manager = window_manager
    
    def open_item(self, name: str, type: str, icon_x: int, icon_y: int):
        """Wrapper around existing open logic - no changes yet"""
        # Copy exact logic from main.py open_item
        content = CreateContent(name, type)
        window_data = self.window_manager.create_window(name, content, icon_x, icon_y)

        if window_data is None:
            print(f"Window {name} already exists - ignoring click")
            return None, None

        window = Window(window_data)

        if type == "folder":
            updated_icon = DesktopIcon(name, type, oob_update=True)
            return window, updated_icon

        return window, None
    
    
    def minimize_window(self, window_id: str):
        """Move minimize logic to service layer"""
        position = self.window_manager.minimize_window(window_id)
        window_data = self.window_manager.get_window(window_id)

        if not window_data or position is None:
            return None

        # Calculate taskbar position using configuration
        left, bottom = self.window_manager.calculate_taskbar_position(position)

        # Return the exact same Div structure as before
        from fasthtml.common import Div, Span, Button
        
        return Div(
            Div(
                Span("■", cls="minimized-icon"),
                Span(window_data['name'], cls="minimized-title"),
                Button("^", cls="restore-button",
                    hx_post=f"/window/{window_id}/restore",
                    hx_target=f"#{window_id}",
                    hx_swap="outerHTML"),
                cls="minimized-window"
            ),
            id=window_id,
            cls="minimized-container",
            style=f"position: absolute; left: {left}px; bottom: {bottom}px; z-index: 50;"
        )

    def restore_window(self, window_id: str):
        """Move restore logic to service layer"""
        window_data = self.window_manager.restore_window(window_id)
        
        if not window_data:
            return None
        
        return Window(window_data)
    
    def maximize_window(self, window_id: str):
        """Move maximize logic to service layer"""
        window_data = self.window_manager.maximize_window(window_id)
        
        if not window_data:
            return None
        
        return Window(window_data, maximized=True)
    
    def close_window(self, window_id: str):
        """Move close logic to service layer"""
        # Clean up window state
        closed_window_data = self.window_manager.close_window(window_id)

        # If folder was closed, return updated icon via OOB
        if (closed_window_data and
            closed_window_data.get('item_type') == 'folder' and
            closed_window_data['name'] in ICON_POSITIONS):

            return DesktopIcon(closed_window_data['name'], 'folder', oob_update=True)

        return None
    
    def move_window(self, window_id: str, x: int, y: int):
        """Move window position logic to service layer"""
        success = self.window_manager.update_window_position(window_id, x, y)
        return success

# Global instance
desktop_service = DesktopService()