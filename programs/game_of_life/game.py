"""
Conway's Game of Life - Core Logic
"""

class GameOfLife:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(width)] for _ in range(height)]
        self.generation = 0
        self.running = False
        self.auto_running = False  # NEW: Track auto-run state

        # Add some initial patterns for demo
        self._add_glider(2, 2)
        self._add_blinker(10, 7)
    
    def _add_glider(self, x, y):
        """Add a glider pattern at position (x, y)"""
        pattern = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        for dx, dy in pattern:
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                self.grid[y + dy][x + dx] = True
    
    def _add_blinker(self, x, y):
        """Add a blinker pattern at position (x, y)"""
        pattern = [(0, 0), (1, 0), (2, 0)]
        for dx, dy in pattern:
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                self.grid[y + dy][x + dx] = True
    
    def get_neighbors(self, x, y):
        """Count living neighbors around cell (x, y)"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx]:
                        count += 1
        return count
    
    def step(self):
        """Advance one generation using Conway's rules"""
        new_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.get_neighbors(x, y)
                current = self.grid[y][x]
                
                # Conway's rules
                if current and neighbors in [2, 3]:
                    new_grid[y][x] = True  # Survive
                elif not current and neighbors == 3:
                    new_grid[y][x] = True  # Birth
                # Otherwise cell dies or stays dead
        
        self.grid = new_grid
        self.generation += 1
    
    def toggle_cell(self, x, y):
        """Toggle cell state at position (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]
    
    def clear(self):
        """Clear all cells"""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
    
    def get_live_cell_count(self):
        """Get total number of living cells"""
        return sum(sum(row) for row in self.grid)
    
    def start_auto_run(self):
        """Start auto-running the simulation"""
        self.auto_running = True
        self.running = True
    
    def stop_auto_run(self):
        """Stop auto-running the simulation"""
        self.auto_running = False
        self.running = False
    
    def toggle_auto_run(self):
        """Toggle auto-run state"""
        if self.auto_running:
            self.stop_auto_run()
        else:
            self.start_auto_run()
    
    def is_auto_running(self):
        """Check if auto-run is active"""
        return self.auto_running
    
    
# Global game instance - in a real app you'd have per-user instances
game = GameOfLife()