from behave import given, when, then
from app import app

@given("the Mes motor speed is running")
def step_given_app_running(context):
    context.client = app.test_client()

@when('I request the "/ai/motorSpeed" endpoint')
def step_when_request_ping(context):
    context.response = context.client.get("/ai/motorSpeed", headers={"Accept": "text/html"})

@then('I should receive "Motor Speed vs Temperature (AI Analysis)"')
def step_then_receive_pong(context):
    assert "Motor Speed vs Temperature (AI Analysis)" in context.response.get_data(as_text=True)
    assert "<canvas" in context.response.get_data(as_text=True)
    assert "AI Model Insights" in context.response.get_data(as_text=True)
    assert "<table" in context.response.get_data(as_text=True)
    assert "</table>" in context.response.get_data(as_text=True)     