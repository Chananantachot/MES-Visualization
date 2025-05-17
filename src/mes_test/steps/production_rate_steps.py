from behave import given, when, then
from app import app
#-----------------------------------------------
# In order to run these tests, need to run server.py first.
#-----------------------------------------------
@given("the Mes opcua server is running")
def step_given_app_running(context):
    context.client = app.test_client()

@when('I request the "/opcua/products" endpoint')
def step_when_request_ping(context):
    context.response = context.client.get("/opcua/products")

@then('I should receive graph data')
def step_then_receive_pong(context):
    data = context.response.get_json()
    assert "labels" in data
    assert "data" in data
    assert len(data["data"]) > 0

@when('I request the "/productionRates" endpoint')
def step_when_request_ping(context):
    context.response = context.client.get("/productionRates")

@then('I should receive "Visualization of MES Production Rate Simulation"')
def step_then_receive_pong(context):
    assert "Visualization of MES Production Rate Simulation" in context.response.get_data(as_text=True)
    assert "<canvas" in context.response.get_data(as_text=True)
    assert "</canvas>" in context.response.get_data(as_text=True) 