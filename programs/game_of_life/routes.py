# programs/game_of_life/routes.py
import random
from .game import game
from .components import GameOfLifeInterface, GameGrid

def setup_gameoflife_routes(app):
    
    @app.post("/gameoflife/step")
    def step_game():
        """Single step - clean and simple"""
        game.step()
        return GameOfLifeInterface(game)
    
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