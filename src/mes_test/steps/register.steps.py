from behave import given, when, then
from bs4 import BeautifulSoup
import requests
from app import app

@given("the MES register app is running")
def step_impl(context):
    context.client = app.test_client()

@when('I request the "{endpoint}" endpoint')
def step_impl(context,endpoint):
    context.response = context.client.get(endpoint)

@then('I should receive "{text}"')
def step_impl(context,text):
    assert text in context.response.get_data(as_text=True)

@then('the register response status code should be {status_code:d}')
def step_impl(context, status_code):
    print(f"Response status code: {context.response.status_code} == {status_code}")
    
    assert context.response.status_code == status_code

@then('the response body should contain "{text}" and "{field_name}" value in hidden field')
def step_impl(context, text, field_name):
    html = context.response.text
    assert text in html, f"Expected text '{text}' not found in the response" 

    soup = BeautifulSoup(html, 'html.parser')
    userid = soup.find('input', {'type': 'hidden', 'name': field_name})
    assert userid is not None, "User ID not found in the response"
    if userid:
        context.form_data['userid'] = userid['value']
    else:
        context.form_data['userid'] = None
    if context.form_data['userid']:
        context.response = requests.post('/active', data=context.form_data)
        assert context.response.status_code == 200
        assert context.response.text == "OK"      
