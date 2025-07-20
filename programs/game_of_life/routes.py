"""
Game of Life HTMX Routes
Add these routes to your main.py file
"""
import random
from .game import game
from .components import GameContainer, GameGrid

def setup_gameoflife_routes(app):
    """Add Game of Life routes to the FastHTML app"""
    
    @app.post("/gameoflife/step")
    def step_game():
        """Advance one generation"""
        game.step()
        return GameContainer(game)
    
    @app.post("/gameoflife/toggle/{x}/{y}")
    def toggle_cell(x: int, y: int):
        """Toggle a specific cell"""
        game.toggle_cell(x, y)
        return GameGrid(game)
    
    @app.post("/gameoflife/clear")
    def clear_game():
        """Clear the grid"""
        game.clear()
        return GameContainer(game)
    
    @app.post("/gameoflife/random")
    def randomize_game():
        """Fill grid with random pattern"""
        game.clear()
        # Add random living cells (about 30% density)
        for y in range(game.height):
            for x in range(game.width):
                if random.random() < 0.3:
                    game.grid[y][x] = True
        return GameContainer(game)
    
    @app.post("/gameoflife/toggle-autorun")
    def toggle_autorun():
        """Toggle auto-run mode"""
        game.toggle_auto_run()
        return GameContainer(game)
    
    @app.post("/gameoflife/auto-step")
    def auto_step():
        """Auto-step for continuous running"""
        if game.is_auto_running():
            game.step()
        return GameContainer(game)
    