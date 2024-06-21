import asyncio
import click
import yaml

from datetime import datetime, time, timedelta, timezone
from dateutil.parser import parse
from pathlib import Path, PurePath
from rich import print_json

from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import RunCode, Control


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
@click.option('--techniques', help='comma-separated list of techniques', type=str)
@click.pass_obj
@handle_api_error
def list_tests(controller, techniques):
    """ List all security tests """
    with Spinner(description='Fetching all security tests'):
        filters = dict()
        if techniques:
            filters['techniques'] = techniques
        data = controller.list_tests(filters=filters)
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
def list_threats(controller):
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


@detect.command('detections')
@click.pass_obj
@handle_api_error
def list_detections(controller):
    """ List all Prelude detections """
    with Spinner(description='Fetching detections'):
        data = controller.list_detections()
    print_json(data=data)


@detect.command('detection')
@click.argument('detection_id')
@click.option('-s', '--sigma_only', help='output the sigma rule only in yaml format', is_flag=True)
@click.option('-o', '--output_file', help='write the sigma rule to a file in yaml format', type=click.Path(writable=True))
@click.pass_obj
@handle_api_error
def get_detection(controller, detection_id, sigma_only, output_file):
    """ List properties for a detection """
    with Spinner(description='Fetching data for detection'):
        data = controller.get_detection(detection_id=detection_id)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(yaml.safe_dump(data['rule']))

    if sigma_only:
        print(yaml.safe_dump(data['rule']))
    else:
        print_json(data=data)


@detect.command('threat-hunts')
@click.option('--tests', help='comma-separated list of tests', type=str)
@click.pass_obj
@handle_api_error
def list_threat_hunts(controller, tests):
    """ List threat hunts """
    with Spinner(description='Fetching threat hunts'):
        filters = dict()
        if tests:
            filters['tests'] = tests
        data = controller.list_threat_hunts(filters)
    print_json(data=data)


@detect.command('threat-hunt')
@click.argument('threat_hunt_id')
@click.pass_obj
@handle_api_error
def get_threat_hunt(controller, threat_hunt_id):
    """ List properties for a threat hunt """
    with Spinner(description='Fetching data for threat hunt'):
        data = controller.get_threat_hunt(threat_hunt_id=threat_hunt_id)
    print_json(data=data)

@detect.command('do-threat-hunt')
@click.argument('threat_hunt_id')
@click.pass_obj
@handle_api_error
def do_threat_hunt(controller, threat_hunt_id):
    """ Run a threat hunt query """
    with Spinner(description='Running threat hunt'):
        data = controller.do_threat_hunt(threat_hunt_id=threat_hunt_id)
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
            data = controller.schedule([dict(threat_id=id, run_code=run_code, tags=tags)])
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
@click.option('--dos', help='comma-separated list of DOS', type=str)
@click.option('--endpoints', help='comma-separated list of endpoint IDs', type=str)
@click.option('--finish', help='end date of activity (end of day)', type=str)
@click.option('--os', help='comma-separated list of OS', type=str)
@click.option('--policy', help='comma-separated list of policies', type=str)
@click.option('--social', help='whether to fetch account-specific or social stats. Applicable to the following views: protected', is_flag=True)
@click.option('--start', help='start date of activity (beginning of day)', type=str)
@click.option('--statuses', help='comma-separated list of statuses', type=str)
@click.option('--techniques', help='comma-separated list of techniques', type=str)
@click.option('--tests', help='comma-separated list of test IDs', type=str)
@click.option('--threats', help='comma-separated list of threat IDs', type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, control, dos, endpoints, finish, os, policy, social, start, statuses, techniques, tests, threats, view):
    """ View my Detect results """
    start = parse(start) if start else datetime.now(timezone.utc) - timedelta(days=29)
    finish = parse(finish) if finish else datetime.now(timezone.utc)
    filters = dict(
        start=datetime.combine(start, time.min),
        finish=datetime.combine(finish, time.max)
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
    if statuses:
        filters['statuses'] = statuses
    if techniques:
        filters['techniques'] = techniques
    if tests:
        filters['tests'] = tests
    if threats:
        filters['threats'] = threats

    with Spinner(description='Fetching activity'):
        data = controller.describe_activity(view=view, filters=filters)
    print_json(data=data)

@detect.command('threat-hunt-activity')
@click.argument('id')
@click.option('-t', '--type', help='whether you are getting activity for a threat hunt, test, or threat', required=True,
              type=click.Choice(['THREAT_HUNT', 'TEST', 'THREAT'], case_sensitive=False))
@click.pass_obj
@handle_api_error
def threat_hunt_activity(controller, id, type):
    """ Get threat hunt activity """
    with Spinner(description='Fetching threat hunt activity'):
        if type == 'THREAT_HUNT':
            data = controller.threat_hunt_activity(threat_hunt_id=id)
        elif type == 'TEST':
            data = controller.threat_hunt_activity(test_id=id)
        else:
            data = controller.threat_hunt_activity(threat_id=id)
    print_json(data=data)
