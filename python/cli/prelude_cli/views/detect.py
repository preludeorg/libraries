import click
import asyncio 

from rich import print_json
from pathlib import Path, PurePath
from datetime import datetime, timedelta, timezone, time

from prelude_sdk.models.codes import RunCode, Control
from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.detect_controller import DetectController


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuous security testing """
    ctx.obj = DetectController(account=ctx.obj)


@detect.command('create-endpoint')
@click.option('-h', '--host', help='hostname of this machine', type=str, required=True)
@click.option('-s', '--serial_num', help='serial number of this machine', type=str, required=True)
@click.option('-t', '--tags', help='a comma-separated list of tags for this endpoint', type=str, default=None)
@click.pass_obj
@handle_api_error
def register_endpoint(controller, host, serial_num, tags):
    """ Register a new endpoint """
    with Spinner(description='Registering endpoint'):
        token = controller.register_endpoint(
            host=host,
            serial_num=serial_num,
            tags=tags
        )
    click.secho(token)


@detect.command('update-endpoint')
@click.argument('endpoint_id')
@click.option('-t', '--tags', help='a comma-separated list of tags for this endpoint', type=str, default=None)
@click.pass_obj
@handle_api_error
def update_endpoint(controller, endpoint_id, tags):
    """ Update an existing endpoint """
    with Spinner(description='Updating endpoint'):
        data = controller.update_endpoint(endpoint_id=endpoint_id, tags=tags)
    print_json(data=data)


@detect.command('tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ List all security tests """
    with Spinner(description='Fetching all security tests'):
        data = controller.list_tests()
    print_json(data=data)


@detect.command('test')
@click.argument('test_id')
@click.pass_obj
@handle_api_error
def get_test(controller, test_id):
    """ List properties for a test """
    with Spinner(description='Fetching data for test'):
        data = controller.get_test(test_id=test_id)
    print_json(data=data)


@detect.command('threats')
@click.pass_obj
@handle_api_error
def threats(controller):
    """ List all Prelude threats """
    with Spinner(description='Fetching threats'):
        data = controller.list_threats()
    print_json(data=data)


@detect.command('threat')
@click.argument('threat_id')
@click.pass_obj
@handle_api_error
def get_threat(controller, threat_id):
    """ List properties for a threat """
    with Spinner(description='Fetching data for threat'):
        data = controller.get_threat(threat_id=threat_id)
    print_json(data=data)


@detect.command('download')
@click.argument('test')
@click.pass_obj
@handle_api_error
def download(controller, test):
    """ Download a test to your local environment """
    click.secho(f'Downloading {test}')
    Path(test).mkdir(parents=True, exist_ok=True)
    with Spinner(description='Downloading test'):
        attachments = controller.get_test(test_id=test).get('attachments')

        for attach in attachments:
            code = controller.download(test_id=test, filename=attach)
            with open(PurePath(test, attach), 'wb') as f:
                f.write(code)


@detect.command('schedule')
@click.argument('id')
@click.option('-t', '--type', help='whether you are scheduling a test or threat', required=True,
              type=click.Choice(['TEST', 'THREAT'], case_sensitive=False))
@click.option('--tags', help='only enable for these tags (comma-separated list)', type=str, default='')
@click.option('-r', '--run_code',
              help='provide a run_code',
              default=RunCode.DAILY.name, show_default=True,
              type=click.Choice([r.name for r in RunCode if r != RunCode.INVALID], case_sensitive=False))
@click.pass_obj
@handle_api_error
def schedule(controller, id, type, run_code, tags):
    """ Add test or threat to your queue """
    with Spinner(description=f'Scheduling {type.lower()}'):
        if type == 'TEST':
            data = controller.schedule([dict(test_id=id, run_code=run_code, tags=tags)])
        else:
            data = controller.schedule([dict(test_id=id, run_code=run_code, tags=tags)])
    print_json(data=data)


@detect.command('unschedule')
@click.argument('id')
@click.option('-t', '--type', help='whether you are unscheduling a test or threat', required=True,
              type=click.Choice(['TEST', 'THREAT'], case_sensitive=False))
@click.option('--tags', help='only disable for these tags (comma-separated list)', type=str, default='')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def unschedule(controller, id, type, tags):
    """ Remove test or threat from your queue """
    with Spinner(description=f'Unscheduling {type.lower()}'):
        if type == 'TEST':
            data = controller.unschedule([dict(test_id=id, tags=tags)])
        else:
            data = controller.unschedule([dict(threat_id=id, tags=tags)])
    print_json(data=data)


@detect.command('delete-endpoint')
@click.argument('endpoint_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_endpoint(controller, endpoint_id):
    """Delete a probe/endpoint"""
    with Spinner(description='Deleting endpoint'):
        data = controller.delete_endpoint(ident=endpoint_id)
    print_json(data=data)


@detect.command('queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ List all tests in your active queue """
    with Spinner(description='Fetching active tests from queue'):
        iam = IAMController(account=controller.account)
        data = iam.get_account().get('queue')
    print_json(data=data)


@detect.command('endpoints')
@click.option('-d', '--days', help='only show endpoints that have run at least once in the past DAYS days', default=90, type=int)
@click.pass_obj
@handle_api_error
def endpoints(controller, days):
    """ List all active endpoints associated to your account """
    with Spinner(description='Fetching endpoints'):
        data = controller.list_endpoints(days=days)
    print_json(data=data)


@detect.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Download all tests to your local environment """
    
    async def fetch(test):
        click.secho(f'Cloning {test["id"]}')
        Path(test['id']).mkdir(parents=True, exist_ok=True)

        for attach in controller.get_test(test_id=test['id']).get('attachments'):
            code = controller.download(test_id=test['id'], filename=attach)
            with open(PurePath(test['id'], attach), 'wb') as f:
                f.write(code)

    async def start_cloning():
        await asyncio.gather(*[fetch(test) for test in controller.list_tests()])

    with Spinner(description='Downloading all tests'):
        asyncio.run(start_cloning())
    click.secho('Project cloned successfully', fg='green')


@detect.command('activity')
@click.option('--view',
              help='retrieve a specific result view',
              default='logs', show_default=True,
              type=click.Choice(['endpoints', 'findings', 'logs', 'metrics', 'protected', 'techniques', 'tests', 'threats']))
@click.option('--control', type=click.Choice([c.name for c in Control], case_sensitive=False))
@click.option('--days', help='days to look back (max: 29)', default=29, type=int)
@click.option('--dos', help='comma-separated list of DOS', type=str)
@click.option('--endpoints', help='comma-separated list of endpoint IDs', type=str)
@click.option('--os', help='comma-separated list of OS', type=str)
@click.option('--policy', help='comma-separated list of policies', type=str)
@click.option('--social', help='whether to fetch account-specific or social stats. Applicable to the following views: protected', is_flag=True)
@click.option('--techniques', help='comma-separated list of techniques', type=str)
@click.option('--tests', help='comma-separated list of test IDs', type=str)
@click.option('--threats', help='comma-separated list of threat IDs', type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, control, days, dos, endpoints, os, policy, social, techniques, tests, threats, view):
    """ View my Detect results """
    filters = dict(
        start=datetime.combine(datetime.now(timezone.utc) - timedelta(days=min(days, 29)), time.min),
        finish=datetime.combine(datetime.now(timezone.utc), time.max)
    )
    if control:
        filters['control'] = Control[control.upper()].value
    if dos:
        filters['dos'] = dos
    if endpoints:
        filters['endpoints'] = endpoints
    if os:
        filters['os'] = os
    if policy:
        filters['policy'] = policy
    if social:
        filters['impersonate'] = 'social'
    if techniques:
        filters['techniques'] = techniques
    if tests:
        filters['tests'] = tests
    if threats:
        filters['threats'] = threats

    with Spinner(description='Fetching activity'):
        data = controller.describe_activity(view=view, filters=filters)
    print_json(data=data)
