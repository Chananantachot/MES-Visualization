from behave import given, then
from mes import mes

# Start testing sensor anomaly fuction.
@given("the sensor anomaly function is executed")
def step_impl(context):
    context.table_html, context.sensor_summary = mes.sensor_anomaly()

@then("the sensor anomaly output should include an HTML table")
def step_impl(context):
    assert "<table" in context.table_html
    assert "</table>" in context.table_html


@then("the sensor_summary should contain Anomaly Flag")
def step_impl(context):
    expected_key = "Anomaly Flag"
    assert expected_key in context.sensor_summary
    values = context.sensor_summary[expected_key]
    assert any(cat in values for cat in [1, -1])
