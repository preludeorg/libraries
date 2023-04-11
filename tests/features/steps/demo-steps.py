from behave import *
from prelude_sdk.models.account import Account
from prelude_sdk.controllers.detect_controller import DetectController

@given('I am signed in as a demo user')
def step_impl(context):
    # No-op:  Tests are always available to an account
    context.controller = DetectController(account=Account())

# --- Activity data scenarios ---

@given('I want to request activity data from the "{view}" view')
def step_impl(context, view):
    context.controller = DetectController(account=Account())
    context.view = view
    context.options = {}

@given('I specify a test ID "{test}"')
def step_impl(context, test):
    context.options["tests"] = [test]

@given('I specify a DOS "{dos}"')
def step_impl(context, dos):
    context.options["dos"] = [dos]

@given('I specify a tag "{tag}"')
def step_impl(context, tag):
    context.options["tags"] = [tag]

@when('I retrieve the activity data')
def step_impl(context):
    context.response = context.controller.describe_activity(filters=context.options, view=context.view)

@then('the response should contain logs')
def step_impl(context):
    assert isinstance(context.response, list)
    assert len(context.response) > 0
    assert "id" in context.response[0]
    assert "date" in context.response[0]
    assert "test" in context.response[0]
    assert "endpoint_id" in context.response[0]
    assert "status" in context.response[0]
    assert "dos" in context.response[0]
    assert "tags" in context.response[0]
    assert "edr_id" in context.response[0]

@then('the response should contain data only for that test ID')
def step_impl(context):
    assert all(ele["test"] == context.options["tests"][0] for ele in context.response)

@then('the response should contain data only for that tag')
def step_impl(context):
    assert all(ele["tags"][0] == context.options["tags"][0] for ele in context.response)

@then('the response should contain data only for that DOS')
def step_impl(context):
    assert all(ele["dos"] == context.options["dos"][0] for ele in context.response)

@then('the response should contain insights')
def step_impl(context):
    assert isinstance(context.response, list)
    assert len(context.response) > 0
    assert "dos" in context.response[0]
    assert "test" in context.response[0]
    assert "volume" in context.response[0]
    assert "error" in context.response[0]['volume']
    assert "protected" in context.response[0]['volume']
    assert "unprotected" in context.response[0]['volume']


@then('the response should contain probes')
def step_impl(context):
    assert isinstance(context.response, list)
    assert len(context.response) > 0
    assert "endpoint_id" in context.response[0]
    assert "dos" in context.response[0]
    assert "tags" in context.response[0]
    assert "state" in context.response[0]
    assert "edr_id" in context.response[0]

@then('the response should contain rules')
def step_impl(context):
    assert isinstance(context.response, list)
    assert len(context.response) > 0
    assert "rule" in context.response[0]
    assert "id" in context.response[0]['rule']
    assert "label" in context.response[0]['rule']
    assert "published" in context.response[0]['rule']
    assert "description" in context.response[0]['rule']
    assert "long_description" in context.response[0]['rule']

#  --- Scenario: Get tests ---

@when('I retrieve tests')
def step_impl(context):
    context.response = context.controller.list_tests()

@then('the response should contain tests')
def step_impl(context):
    assert isinstance(context.response, list)
    assert len(context.response) > 0
    assert "id" in context.response[0]
    assert "name" in context.response[0]
    assert "account_id" in context.response[0]

# --- Scenario: Search the NVD for a keyword ---

@given('I have a keyword to search for "{text}"')
def step_impl(context, text):
    context.keyword = text

@when('I search for the keyword')
def step_impl(context):
    context.response = context.controller.search(identifier=context.keyword)

@then('the response should contain search results')
def step_impl(context):
    assert 'info' in context.response
    assert 'tests' in context.response