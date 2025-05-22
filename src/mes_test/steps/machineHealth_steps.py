from behave import given, then
from mes import mes

@given("the machine health function is executed")
def step_impl(context):
    context.table_html, context.machine_data = mes.machine_health()

@then("the machine health output should include an HTML table")
def step_impl(context):
    assert "<table" in context.table_html
    assert "</table>" in context.table_html

@then("the summary should contain Failure Risk")
def step_impl(context):
    expected_key =  "Failure_Risk"
    assert expected_key in context.machine_data
    values = context.machine_data[expected_key]
    assert any(cat in values for cat in [0, 1])  