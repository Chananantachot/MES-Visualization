from behave import given, then
from app import production_slowdown

# Start testing production slowdown fuction.
@given("the production slowdown function is executed")
def step_impl(context):
    context.table_html, context.summary = production_slowdown()

@then("the output should include an HTML table")
def step_impl(context):
    assert "<table" in context.table_html
    assert "</table>" in context.table_html

@then("the summary should contain impact levels")
def step_impl(context):
    expected_keys = ["Shift Impact", "Temp Impact", "Humidity Impact"]
    for key in expected_keys:
        assert key in context.summary
        values = context.summary[key]
        assert any(cat in values for cat in ['Low', 'Medium', 'High'])
