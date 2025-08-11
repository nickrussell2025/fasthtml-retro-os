# programs/game_of_life/components.py
from fasthtml.common import *
from functools import lru_cache


def GameContainer(game):
    """Main entry point - matches your existing code"""
    return GameOfLifeInterface(game)

@lru_cache(maxsize=30)
def cached_game_interface(generation: int, live_cells: int):
    """Cache the static parts of the interface"""
    return {
        'title': H3("Conway's Game of Life", style="text-align: center; margin-bottom: 10px; color: var(--primary-color);"),
        'status': Div(f"Generation: {generation} • Live cells: {live_cells}",
                     style="text-align: center; margin-bottom: 10px; font-size: 12px; color: var(--primary-color);"),
        'controls': GameControls()
    }

def GameOfLifeInterface(game):
    """Clean, simple game interface - now with caching"""
    # Get cached components
    cached = cached_game_interface(game.generation, game.get_live_cell_count())
    
    return Div(
        cached['title'],
        cached['status'],
        
        # Game grid (can't cache this effectively since it changes)
        Div(
            GameGrid(game),
            style="display: flex; flex-direction: column; align-items: center; margin: 15px 0; border: 2px solid var(--primary-color); padding: 5px; background: rgba(0, 0, 0, 0.3);"
        ),
        
        cached['controls'],
        style="padding: 15px;"
    )

def GameGrid(game):
    """Generate clickable grid from game state"""
    rows = []
    for y in range(game.height):
        cells = []
        for x in range(game.width):
            cell_color = "var(--primary-color)" if game.grid[y][x] else "transparent"
            cells.append(
                Div(
                    hx_post=f"/gameoflife/toggle/{x}/{y}",
                    hx_target="closest .window-content",  # Replace entire game interface
                    hx_swap="innerHTML",
                    style=f"""
                        width: 15px; 
                        height: 15px; 
                        border: 1px solid var(--primary-dim); 
                        cursor: pointer; 
                        background: {cell_color};
                    """
                )
            )
        rows.append(Div(*cells, style="display: flex;"))
    return Div(*rows)

def GameControls():
    """Basic game controls - no auto-run"""
    return Div(
        Button("⏭️ Step", 
               hx_post="/gameoflife/step",
               hx_target="closest .window-content",
               hx_swap="innerHTML",
               style="background: var(--primary-color); color: var(--bg-black); border: none; padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        Button("🗑️ Clear", 
               hx_post="/gameoflife/clear",
               hx_target="closest .window-content", 
               hx_swap="innerHTML",
               style="background: var(--primary-dark); color: var(--primary-color); border: 1px solid var(--primary-color); padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        Button("🎲 Random", 
               hx_post="/gameoflife/random",
               hx_target="closest .window-content",
               hx_swap="innerHTML", 
               style="background: var(--primary-dark); color: var(--primary-color); border: 1px solid var(--primary-color); padding: 8px 12px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;"),
        
        style="text-align: center; margin-top: 15px;"
    )