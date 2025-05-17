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