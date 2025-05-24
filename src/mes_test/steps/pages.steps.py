from behave import given, when, then
import requests
from app import app


@when('i make a request to "{endpoint}"')
def step_impl(context, endpoint):
    context.response = requests.get(endpoint)
   
@when('I make a request to "{endpoint}" API endpoint')
def step_impl(context, endpoint):
    context.client = app.test_client()
    context.response = context.client.get(endpoint, headers={"Accept": "application/json"})

@then('I should receive json data back')
def step_impl(context):
    print(f"Expected status code 200, but got {context.response.status_code}")
    assert context.response.status_code == 200, f"Expected status code 200, but got {context.response.status_code}"
    assert context.response.headers['Content-Type'] == 'application/json', f"Expected JSON response, but got {context.response.headers['Content-Type']}" 
    assert "labels" in context.response.json   # Ensure the response contains 'labels'    
    assert "datasets" in context.response.json    
    assert len(context.response.json["datasets"]) > 0

    print(f"Response JSON: {context.response.json()}")
    
