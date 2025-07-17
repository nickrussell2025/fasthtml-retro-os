from fasthtml.common import *
from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def test_home_normal():
    response = client.get("/")
    print("normal request")
    print(response.text[:200])
    
def test_home_htmx():
    response = client.get("/", headers={"HX-REQUEST": "1"})
    print("HTMX request:")
    print(response.text[:200])
    
    
test_home_normal()
test_home_htmx()