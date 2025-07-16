from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get(): 
    return Div(
        P("hello...world", hx_get="/change", hx_target="#display"),
        Div(id="display")
    )

@rt('/change')
def change(): 
    return Div(
        P("you clicked it"),
        Button("click on me again", hx_get="/another", hx_target="#display")
    )

@rt('/another')
def another(): 
    return Div(
        P("another message"),
        Button("go back", hx_get="/change", hx_target="#display")
    )
    
@rt("/form")
def form_page():
    return Form(
        Input(name="message", placeholder="Type something"),
        Button("Send"),
        hx_post="/handle_form",
        hx_target="#result"
    ), Div(id="result")
    
@rt("/handle_form")
def handle_form(message: str):
    return P(f"You typed: {message}")

serve()