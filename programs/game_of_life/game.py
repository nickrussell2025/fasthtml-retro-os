# programs/game_of_life/game.py

class GameOfLife:
    """Optimized Game of Life - using efficient neighbor calculation"""
    
    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.generation = 0
        self.grid = [[False for _ in range(width)] for _ in range(height)]
        
        # Pre-calculate neighbor offsets once
        self.neighbor_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
    
    def step(self):
        """Optimized step function - single pass, minimal allocations"""
        # Pre-allocate the new grid
        new_grid = [[False] * self.width for _ in range(self.height)]
        
        # Single pass through the grid
        for y in range(self.height):
            for x in range(self.width):
                # Count neighbors inline
                neighbors = 0
                for dx, dy in self.neighbor_offsets:
                    nx, ny = x + dx, y + dy
                    # Bounds check and count in one condition
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx]:
                        neighbors += 1
                
                # Apply rules directly
                if self.grid[y][x]:
                    new_grid[y][x] = neighbors in (2, 3)
                else:
                    new_grid[y][x] = neighbors == 3
        
        self.grid = new_grid
        self.generation += 1
    
    def toggle_cell(self, x: int, y: int):
        """Toggle cell state at position (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]
    
    def clear(self):
        """Clear all cells and reset generation"""
        self.grid = [[False] * self.width for _ in range(self.height)]
        self.generation = 0
    
    def get_live_cell_count(self) -> int:
        """Get total number of living cells"""
        return sum(sum(row) for row in self.grid)

# Global game instance
game = GameOfLife()