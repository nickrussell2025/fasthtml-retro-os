from fasthtml.common import *
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    email: str
    age: int

app = FastHTML()
rt = app.route

@rt("/user-test")
def user_test(name: str, email: str, age: str):
    try:
        user = User(name=name, email=email, age=age)
        return P(f"Hello {user.name}, age {user.age}")
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field_name = error['loc'][0]
            message = error['msg']
            errors.append(Li(f"{field_name}: {message}"))
        return Div(P("Please fix these errors:"), Ul(*errors))

serve()