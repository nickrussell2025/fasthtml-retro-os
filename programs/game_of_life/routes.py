# programs/game_of_life/routes.py
import random
from .game import game
from .components import GameOfLifeInterface, GameGrid, Div

def setup_gameoflife_routes(app):
    
    @app.post("/gameoflife/step")
    def step_game():
        """Return minimal HTML - just the changed parts"""
        game.step()
        
        # Build minimal response with just what changed
        status = f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}"
        
        # Return a much smaller payload
        return Div(
            Div(status, style="text-align: center; margin-bottom: 10px; font-size: 12px; color: var(--primary-color);"),
            Div(
                GameGrid(game),
                style="display: flex; flex-direction: column; align-items: center; margin: 15px 0; border: 2px solid var(--primary-color); padding: 5px; background: rgba(0, 0, 0, 0.3);"
            ),
            style="padding: 15px;"
        )
    
    @app.post("/gameoflife/toggle/{x}/{y}")
    def toggle_cell(x: int, y: int):
        """Toggle cell and return full interface"""
        game.toggle_cell(x, y)
        return GameOfLifeInterface(game)
    
    @app.post("/gameoflife/clear")
    def clear_game():
        """Clear grid and return full interface"""
        game.clear()
        return GameOfLifeInterface(game)
    
    @app.post("/gameoflife/random")
    def randomize_game():
        """Randomize grid with 30% density"""
        game.clear()
        for y in range(game.height):
            for x in range(game.width):
                if random.random() < 0.3:
                    game.grid[y][x] = True
        return GameOfLifeInterface(game)