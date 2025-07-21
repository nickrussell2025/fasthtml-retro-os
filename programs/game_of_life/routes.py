import random
from .game import game
from .components import GameContainer, GameGrid

def setup_gameoflife_routes(app):
    
    @app.post("/gameoflife/step")
    def step_game():
        game.step()
        status = f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}"
        grid_html = str(GameGrid(game))
        return f'<div hx-swap-oob="innerHTML:#game-status">{status}</div><div hx-swap-oob="innerHTML:#game-grid">{grid_html}</div>'
    
    @app.post("/gameoflife/toggle/{x}/{y}")
    def toggle_cell(x: int, y: int):
        game.toggle_cell(x, y)
        return GameGrid(game)
    
    @app.post("/gameoflife/clear")
    def clear_game():
        game.clear()
        status = f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}"
        grid_html = str(GameGrid(game))
        return f'<div hx-swap-oob="innerHTML:#game-status">{status}</div><div hx-swap-oob="innerHTML:#game-grid">{grid_html}</div>'
    
    @app.post("/gameoflife/random")
    def randomize_game():
        game.clear()
        for y in range(game.height):
            for x in range(game.width):
                if random.random() < 0.3:
                    game.grid[y][x] = True
        
        status = f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}"
        grid_html = str(GameGrid(game))
        return f'<div hx-swap-oob="innerHTML:#game-status">{status}</div><div hx-swap-oob="innerHTML:#game-grid">{grid_html}</div>'
    
    @app.post("/gameoflife/toggle-autorun")
    def toggle_autorun():
        game.toggle_auto_run()
        return GameContainer(game)
    
    @app.post("/gameoflife/auto-step")
    def auto_step():
        if game.is_auto_running():
            game.step()
            return {
                "running": True,
                "generation": game.generation,
                "live_cells": game.get_live_cell_count(),
                "grid_html": str(GameGrid(game))
            }
        return {"running": False}