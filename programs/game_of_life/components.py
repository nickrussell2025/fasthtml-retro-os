"""
Game of Life FastHTML Components
"""
from fasthtml.common import *

def GameOfLifeInterface(game):
    """Main Game of Life interface"""
    return Div(
        H3("Conway's Game of Life", style="text-align: center; margin-bottom: 10px; color: var(--primary-color);"),
        
        # Game stats
        Div(
            Span(f"Generation: {game.generation}", style="margin-right: 20px;"),
            Span(f"Live cells: {game.get_live_cell_count()}"),
            style="text-align: center; margin-bottom: 10px; font-size: 12px; color: var(--primary-color);"
        ),
        
        # Game grid
        GameGrid(game),
        
        # Control buttons
        GameControls(game),
        
        # Instructions
        Div(
            P("Click cells to toggle • Press Step to advance • Auto-run coming soon!", 
              style="font-size: 11px; color: var(--primary-dim); text-align: center; margin-top: 10px;"),
            style="margin-top: 15px;"
        ),
        
        cls="game-of-life-interface",
        style="padding: 15px;"
    )

def GameGrid(game):
    """Render the game grid with clickable cells"""
    return Div(
        *[
            Div(
                *[
                    Div(
                        cls=f"game-cell {'alive' if game.grid[y][x] else 'dead'}",
                        hx_post=f"/gameoflife/toggle/{x}/{y}",
                        hx_target="#game-grid",
                        hx_swap="outerHTML",
                        style=f"""
                            width: 15px; height: 15px; 
                            border: 1px solid var(--primary-dim);
                            background: {'var(--primary-color)' if game.grid[y][x] else 'transparent'};
                            cursor: pointer;
                            transition: background 0.1s ease;
                        """
                    )
                    for x in range(game.width)
                ],
                style="display: flex;"
            )
            for y in range(game.height)
        ],
        id="game-grid",
        style="""
            display: flex; 
            flex-direction: column; 
            align-items: center;
            margin: 15px 0;
            border: 2px solid var(--primary-color);
            padding: 5px;
            background: rgba(0, 0, 0, 0.3);
        """
    )

def GameControls(game):
    """Game control buttons with auto-run functionality"""
    auto_run_text = "⏸️ Stop" if game.is_auto_running() else "▶️ Auto"
    auto_run_style = """
        background: var(--primary-dark); 
        color: var(--primary-color); 
        border: 1px solid var(--primary-color); 
        padding: 8px 12px; 
        margin: 0 5px;
        border-radius: 4px; 
        cursor: pointer; 
        font-weight: bold;
        font-size: 12px;
    """ if not game.is_auto_running() else """
        background: var(--primary-color); 
        color: var(--bg-black); 
        border: none; 
        padding: 8px 12px; 
        margin: 0 5px;
        border-radius: 4px; 
        cursor: pointer; 
        font-weight: bold;
        font-size: 12px;
    """
    
    return Div(
        Div(
            Button("⏭️ Step", 
                   hx_post="/gameoflife/step",
                   hx_target="#game-container",
                   hx_swap="outerHTML",
                   cls="game-btn",
                   style="""
                       background: var(--primary-color); 
                       color: var(--bg-black); 
                       border: none; 
                       padding: 8px 12px; 
                       margin: 0 5px;
                       border-radius: 4px; 
                       cursor: pointer; 
                       font-weight: bold;
                       font-size: 12px;
                   """),
            
            Button(auto_run_text, 
                   hx_post="/gameoflife/toggle-autorun",
                   hx_target="#game-container",
                   hx_swap="outerHTML",
                   cls="game-btn",
                   style=auto_run_style),
            
            Button("🔄 Clear", 
                   hx_post="/gameoflife/clear",
                   hx_target="#game-container", 
                   hx_swap="outerHTML",
                   cls="game-btn",
                   style="""
                       background: var(--primary-dark); 
                       color: var(--primary-color); 
                       border: 1px solid var(--primary-color); 
                       padding: 8px 12px; 
                       margin: 0 5px;
                       border-radius: 4px; 
                       cursor: pointer; 
                       font-weight: bold;
                       font-size: 12px;
                   """),
            
            Button("🎲 Random", 
                   hx_post="/gameoflife/random",
                   hx_target="#game-container",
                   hx_swap="outerHTML", 
                   cls="game-btn",
                   style="""
                       background: var(--primary-dark); 
                       color: var(--primary-color); 
                       border: 1px solid var(--primary-color); 
                       padding: 8px 12px; 
                       margin: 0 5px;
                       border-radius: 4px; 
                       cursor: pointer; 
                       font-weight: bold;
                       font-size: 12px;
                   """),
            
            style="display: flex; justify-content: center;"
        ),
        style="margin: 15px 0;"
    )
    
def GameOfLifeInterface(game):
    """Main Game of Life interface with auto-run status"""
    status_text = f"Generation: {game.generation} • Live cells: {game.get_live_cell_count()}"
    if game.is_auto_running():
        status_text += " • AUTO-RUNNING"
    
    return Div(
        H3("Conway's Game of Life", style="text-align: center; margin-bottom: 10px; color: var(--primary-color);"),
        
        # Game stats with auto-run indicator
        Div(
            Span(status_text),
            style=f"""text-align: center; margin-bottom: 10px; font-size: 12px; 
                     color: {'var(--primary-color)' if not game.is_auto_running() else 'var(--primary-color)'}; 
                     font-weight: {'normal' if not game.is_auto_running() else 'bold'};"""
        ),
        
        # Game grid
        GameGrid(game),
        
        # Control buttons
        GameControls(game),
        
        # Instructions
        Div(
            P("Click cells to toggle • Step to advance • Auto-run for continuous play!", 
              style="font-size: 11px; color: var(--primary-dim); text-align: center; margin-top: 10px;"),
            style="margin-top: 15px;"
        ),
        
        # Auto-run JavaScript for continuous stepping
        Script(f"""
            if ({str(game.is_auto_running()).lower()}) {{
                setTimeout(() => {{
                    htmx.trigger('#auto-step-trigger', 'click');
                }}, 500);
            }}
        """) if game.is_auto_running() else "",
        
        # Hidden trigger for auto-stepping
        Div(id="auto-step-trigger", 
            hx_post="/gameoflife/auto-step",
            hx_target="#game-container",
            hx_swap="outerHTML",
            style="display: none;"),
        
        cls="game-of-life-interface",
        style="padding: 15px;"
    )


def GameContainer(game):
    """Container wrapper for HTMX updates"""
    return Div(
        GameOfLifeInterface(game),
        id="game-container"
    )