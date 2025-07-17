from fasthtml.common import *

app = FastHTML()

@app.get("/")
def home():
    return "Hello retro OS"

serve()