from behave import given, when, then
import requests

@given('login form endpoint is "{endpoint}"')
def step_impl(context, endpoint):
    context.endpoint = endpoint

@when("submit the login form using POST")
def step_impl(context):
    context.response = requests.post(context.endpoint, data=context.form_data)

@when('i make a request to "{endpoint}"')
def step_impl(context, endpoint):
    context.response = requests.get(endpoint)
   
@then("page response status code should be {status_code:d}")
def step_impl(context, status_code):
    assert context.response.status_code == status_code

@then('page response body should contain "{text}"')
def step_impl(context, text):
    assert text in context.response.text  

