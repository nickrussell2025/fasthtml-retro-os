# programs/game_of_life/components.py
from fasthtml.common import *

def GameOfLifeInterface(game):
    return Div(
        H3("Conway's Game of Life", style="text-align: center; margin-bottom: 10px; color: var(--primary-color);"),
        
        Div(
            f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}" + 
            (" • AUTO-RUNNING" if game.is_auto_running() else ""),
            id="game-status",
            style="text-align: center; margin-bottom: 10px; font-size: 12px; color: var(--primary-color);"
        ),
        
        Div(
            GameGrid(game),
            id="game-grid",
            style="display: flex; flex-direction: column; align-items: center; margin: 15px 0; border: 2px solid var(--primary-color); padding: 5px; background: rgba(0, 0, 0, 0.3);"
        ),
        
        GameControls(game),
        
        # Game manager will handle auto-run - no inline JavaScript needed
        
        style="padding: 15px;"
    )

def GameGrid(game):
    rows = []
    for y in range(game.height):
        cells = []
        for x in range(game.width):
            cells.append(
                Div(
                    hx_post=f"/gameoflife/toggle/{x}/{y}",
                    hx_target="#game-grid",
                    hx_swap="innerHTML",
                    style=f"width: 15px; height: 15px; border: 1px solid var(--primary-dim); cursor: pointer; background: {'var(--primary-color)' if game.grid[y][x] else 'transparent'};"
                )
            )
        rows.append(Div(*cells, style="display: flex;"))
    return Div(*rows)

def GameControls(game):
    auto_text = "⏸️ Stop" if game.is_auto_running() else "▶️ Auto"
    auto_bg = "var(--primary-color)" if game.is_auto_running() else "var(--primary-dark)"
    auto_color = "var(--bg-black)" if game.is_auto_running() else "var(--primary-color)"
    auto_border = "none" if game.is_auto_running() else "1px solid var(--primary-color)"
    
    return Div(
        Button("⏭️ Step", 
               hx_post="/gameoflife/step",
               hx_target="#game-grid,#game-status",
               hx_swap="innerHTML",
               style="background: var(--primary-color); color: var(--bg-black); border: none; padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        Button(auto_text, 
               hx_post="/gameoflife/toggle-autorun",
               hx_target="#game-container",
               hx_swap="outerHTML",
               style=f"background: {auto_bg}; color: {auto_color}; border: {auto_border}; padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        Button("🔄 Clear", 
               hx_post="/gameoflife/clear",
               hx_target="#game-grid,#game-status",
               hx_swap="innerHTML",
               style="background: var(--primary-dark); color: var(--primary-color); border: 1px solid var(--primary-color); padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        Button("🎲 Random", 
               hx_post="/gameoflife/random",
               hx_target="#game-grid,#game-status",
               hx_swap="innerHTML",
               style="background: var(--primary-dark); color: var(--primary-color); border: 1px solid var(--primary-color); padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        style="display: flex; justify-content: center; margin: 15px 0;"
    )

def GameContainer(game):
    return Div(GameOfLifeInterface(game), id="game-container")