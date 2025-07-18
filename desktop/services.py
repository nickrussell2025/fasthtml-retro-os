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
        """Optimized minimize - style-only update"""
        position = self.window_manager.minimize_window(window_id)
        window_data = self.window_manager.get_window(window_id)

        if not window_data or position is None:
            return None

        # Calculate taskbar position
        left, bottom = self.window_manager.calculate_taskbar_position(position)
        
        # Return minimal HTML string instead of full component
        return f'''<div id="{window_id}" hx-swap-oob="true" 
                        class="minimized-container"
                        style="position: absolute; left: {left}px; bottom: {bottom}px; 
                            z-index: 50; width: 200px; height: 30px;">
                    <div class="minimized-window">
                    <span class="minimized-icon">■</span>
                    <span class="minimized-title">{window_data['name']}</span>
                    <button class="restore-button" 
                            hx-post="/window/{window_id}/restore"
                            hx-target="#{window_id}" 
                            hx-swap="outerHTML">^</button>
                    </div>
                </div>'''

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