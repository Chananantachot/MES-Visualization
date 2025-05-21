from behave import given, when, then
import requests
from app import app

@given("the MES register app is running")
def step_impl(context):
    context.client = app.test_client()

@when('I request the "/register" endpoint')
def step_impl(context):
    context.response = context.client.get("/signin")

@then('I should receive "Register account"')
def step_impl(context):
    assert "Sign in to continue to Fake it easy" in context.response.get_data(as_text=True)

@given('the register form endpoint is "{endpoint}"')
def step_impl(context, endpoint):
    context.endpoint = endpoint
    
@given(u'the following register form data:')
def step_impl(context):
    context.form_data = {}
    for row in context.table:
        context.form_data[row['name']] = row[row['name']]

@when("I submit the register form using POST")
def step_impl(context):
    context.response = requests.post(context.endpoint, data=context.form_data)

@then("the signin response status code should be {status_code:d}")
def step_impl(context, status_code):
    assert context.response.status_code == status_code

@then('the signin response body should contain "{text}"')
def step_impl(context, text):
    assert text in context.response.text

@then("the register response status code should be {status_code:d}")
def step_impl(context, status_code):
    assert context.response.status_code == status_code

@then('the register response body should contain "{text}"')
def step_impl(context, text):
    assert text in context.response.text        
