from behave import given, when, then
import sys
import os

# Add the src/ directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app

@given("the MES app is running")
def step_given_app_running(context):
    context.client = app.test_client()

@when('I request the "/" endpoint')
def step_when_request_ping(context):
    context.response = context.client.get("/")

@then('I should receive "{expected}"')
def step_then_receive_pong(context,expected):
    assert expected in context.response.get_data(as_text=True)