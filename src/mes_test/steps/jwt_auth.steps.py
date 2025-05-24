from behave import given, when, then
import requests

@then('the cookie "access_token_cookie" should be set expried')
def step_impl(context):
    cookie = context.response.cookies.get("access_token_cookie")
    assert cookie is not None
    assert "expires" in context.response.headers["Set-Cookie"]
    expires = context.response.headers["Set-Cookie"].split("expires=")[1].split(";")[0]
    assert expires is not None
    assert "Max-Age=1800" in context.response.headers["Set-Cookie"]
    assert "Path=/; HttpOnly" in context.response.headers["Set-Cookie"]    

@then('the cookie "{access_token_cookie}" should be set')
def step_impl(context,access_token_cookie):
    cookies = context.response.cookies
    assert access_token_cookie in cookies.keys()
    assert cookies[access_token_cookie] is not None

@when('I send a POST request to "/logout"')
def send_logout_request(context):
    logout_endpoint = context.endpoint.replace("signin", "logout")
    context.response = requests.post(logout_endpoint, cookies=context.response.cookies)

@then('the response should not contain the "{access_token_cookie}" cookie')
def step_impl(context, access_token_cookie):
    assert access_token_cookie not in context.response.cookies.keys()
    