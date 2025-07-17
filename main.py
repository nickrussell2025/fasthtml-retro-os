from fasthtml.common import *
from pydantic import BaseModel, ValidationError


def validation_error_handler(req, exc):
    errors = []
    for error in exc.errors():
        error_type = error['type']
        field_name = error['loc'][0]
        message = error['msg']
        user_input = error['input']
        errors.append(Li(f"{field_name}: {message}"))
        
    return Div(
        P("fix these errors"),
        Ul(*errors)
    )
    
def general_exception_handler(req, exc):
    return P(f"Caught exception: {type(exc).__name__}")

app, rt = fast_app(exception_handlers={
    Exception: general_exception_handler,
    ValidationError: validation_error_handler
})

class User(BaseModel):
    name: str
    email: str
    age: int

@rt('/')
def get(): 
    return Titled("My FastHTML App", 
              P("hello...world", hx_get="/change", target_id="display"),
              Div(id="display"))

@rt('/change')
def change(): 
    return Div(
        P("you clicked it"),
        Button("click on me again", hx_get="/another", target_id="display")
    )

@rt('/another')
def another(): 
    return Div(
        P("another message"),
        Button("go back", hx_get="/change", target_id="display")
    )
    
@rt("/form")
def form_page():
    return Form(
        Hidden(name="session_id", value="user123"),
        CheckboxX(name="urgent", label="mark as urgent"),
        Group(Input(name="message", id="msg-input", placeholder="Type something"), Button("Send")),
        hx_post="/handle_form",
        target_id="result"
    ), Div(id="result")
    
@rt("/handle_form")
def handle_form(message: str, session_id: str, urgent: str):
    if urgent:
        result =  P(f"URGENT FROM {session_id} typed: {message}")
    else:
        result =  P(f"normal from {session_id} typed: {message}")
    
    clear_input = Input(name="message", id="msg-input", placeholder="type something", hx_swap_oob="true")
    
    return result, clear_input

@rt("/test-validation")
def test_validation(age: int):
    return P(f"your name is {age}")

@rt("/user-test")
def user_test(user: User):
    return P(f"hello {user.name}, age {user.age}")

@rt("/debug-validation")
def debug_validation():
    try:
        user = User(name="John", email="john@test.com", age="hello")
        return P("Success")
    except Exception as e:
        return P(f"Exception type: {type(e).__name__}, Message: {str(e)}")


serve()