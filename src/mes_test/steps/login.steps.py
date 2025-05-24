import os
import sys
from behave import given, when, then
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app import app

@given('the MES Login app is running')
def step_impl(context):
    context.client = app.test_client()

@given('the form endpoint is "{endpoint}"')
def step_impl(context, endpoint):
    context.endpoint = endpoint
    
@given(u'the following form data:')
def step_impl(context):
    context.form_data = {}
    for row in context.table:
        context.form_data[row['field']] = row['value']   

@when('I submit the form using POST')
def step_impl(context):
    print(f"Submitting form to endpoint: {context.endpoint} with data: {context.form_data}")
    # Make sure the endpoint is a full URL
    context.response = requests.post(context.endpoint, data=context.form_data)

@then('the response status code should be {status_code:d}')
def step_impl(context, status_code):
    print(f"Expected status code: {status_code}, Actual status code: {context.response.status_code}")
    assert context.response.status_code == status_code, f"Expected status code {status_code}, but got {context.response.status_code}" 

@then('the response body should contain "{text}"')
def step_impl(context, text):
    assert text in context.response.text, f"Expected response body to contain '{text}', but it did not."        

@then(u'the cookie "access_token_cookie" should not be present')
def step_impl(context):
    cookies = context.response.cookies
    assert "access_token_cookie" not in cookies, "Cookie 'access_token_cookie' should not be present in the response."
    
