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
        
        # RESTORE the working inline JavaScript - with Python/JS conversion fix
        Script(f"""
            console.log('Auto-run status:', {str(game.is_auto_running()).lower()});
            
            if ({str(game.is_auto_running()).lower()}) {{
                if (window.golInterval) clearInterval(window.golInterval);
                
                let generation = {game.generation};
                let grid = {str(game.grid).replace('True', 'true').replace('False', 'false')};
                const height = {game.height};
                const width = {game.width};
                
                console.log('Starting auto-run...');
                
                window.golInterval = setInterval(() => {{
                    console.log('Auto-run step:', generation);
                    
                    // Conway's rules
                    const newGrid = [];
                    for (let y = 0; y < height; y++) {{
                        newGrid[y] = [];
                        for (let x = 0; x < width; x++) {{
                            let neighbors = 0;
                            for (let dy = -1; dy <= 1; dy++) {{
                                for (let dx = -1; dx <= 1; dx++) {{
                                    if (dx === 0 && dy === 0) continue;
                                    const ny = y + dy, nx = x + dx;
                                    if (ny >= 0 && ny < height && nx >= 0 && nx < width && grid[ny][nx]) {{
                                        neighbors++;
                                    }}
                                }}
                            }}
                            newGrid[y][x] = grid[y][x] ? (neighbors === 2 || neighbors === 3) : (neighbors === 3);
                        }}
                    }}
                    
                    grid = newGrid;
                    generation++;
                    
                    // Update status
                    const statusEl = document.getElementById('game-status');
                    if (statusEl) {{
                        const liveCount = grid.flat().filter(c => c).length;
                        statusEl.textContent = `Generation: ${{generation}} • Live cells: ${{liveCount}} • AUTO-RUNNING`;
                    }}
                    
                    // Update grid
                    const gridEl = document.getElementById('game-grid');
                    if (gridEl) {{
                        let html = '';
                        for (let y = 0; y < height; y++) {{
                            html += '<div style="display: flex;">';
                            for (let x = 0; x < width; x++) {{
                                const bg = grid[y][x] ? 'var(--primary-color)' : 'transparent';
                                html += `<div onclick="htmx.ajax('POST', '/gameoflife/toggle/${{x}}/${{y}}', {{target: '#game-grid', swap: 'innerHTML'}})" style="width: 15px; height: 15px; border: 1px solid var(--primary-dim); cursor: pointer; background: ${{bg}};"></div>`;
                            }}
                            html += '</div>';
                        }}
                        gridEl.innerHTML = html;
                    }}
                }}, 500);
            }}
        """),
        
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