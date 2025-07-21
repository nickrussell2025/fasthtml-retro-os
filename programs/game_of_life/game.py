# programs/game_of_life/game.py
class GameOfLife:
    """Simplified Game of Life - no auto-run complexity"""
    
    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.generation = 0
        self.grid = [[False for _ in range(width)] for _ in range(height)]
    
    def get_neighbors(self, x: int, y: int) -> int:
        """Count living neighbors for cell at (x, y)"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
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
                
                if self.grid[y][x]:  # Living cell
                    # Survive if 2 or 3 neighbors
                    new_grid[y][x] = neighbors in [2, 3]
                else:  # Dead cell
                    # Birth if exactly 3 neighbors
                    new_grid[y][x] = neighbors == 3
        
        self.grid = new_grid
        self.generation += 1
    
    def toggle_cell(self, x: int, y: int):
        """Toggle cell state at position (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]
    
    def clear(self):
        """Clear all cells and reset generation"""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
    
    def get_live_cell_count(self) -> int:
        """Get total number of living cells"""
        return sum(sum(row) for row in self.grid)

# Global game instance
game = GameOfLife()