import click
import asyncio 

from rich import print_json
from pathlib import Path, PurePath
from datetime import datetime, timedelta

from prelude_sdk.models.codes import RunCode
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
@click.option('-e', '--edr_id', help='EDR id', type=str, default='')
@click.option('-t', '--tags', help='a comma-separated list of tags for this endpoint', type=str, default='')
@click.option('-i', '--endpoint_id', help='update a specific endpoint_id with the provided values', type=str, default='')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, host, serial_num, edr_id, tags, endpoint_id):
    """ Register a new endpoint """
    with Spinner():
        token = controller.register_endpoint(
            host=host, 
            serial_num=serial_num, 
            edr_id=edr_id, 
            tags=tags, 
            endpoint_id=endpoint_id
        )
        click.secho(token)


@detect.command('tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ List all security tests """
    with Spinner():
        data = controller.list_tests()
    print_json(data=data)


@detect.command('test')
@click.argument('test_id')
@click.pass_obj
@handle_api_error
def get_test(controller, test_id):
    """ List properties for a test """
    with Spinner():
        print_json(data=controller.get_test(test_id=test_id))


@detect.command('download')
@click.argument('test')
@click.pass_obj
@handle_api_error
def download(controller, test):
    """ Download a test to your local environment """
    click.secho(f'Downloading {test}')
    Path(test).mkdir(parents=True, exist_ok=True)
    with Spinner():
        attachments = controller.get_test(test_id=test).get('attachments')

        for attach in attachments:
            if Path(attach).suffix:
                code = controller.download(test_id=test, filename=attach)
                with open(PurePath(test, attach), 'wb') as f:
                    f.write(code)


@detect.command('enable-test')
@click.argument('test')
@click.option('-t', '--tags', help='only enable for these tags (comma-separated list)', type=str, default='')
@click.option('-r', '--run_code',
              help='provide a run_code',
              default=RunCode.DAILY.name, show_default=True,
              type=click.Choice([r.name for r in RunCode], case_sensitive=False))
@click.pass_obj
@handle_api_error
def enable_test(controller, test, run_code, tags):
    """ Add test to your queue """
    with Spinner():
        controller.enable_test(ident=test, run_code=RunCode[run_code.upper()].value, tags=tags)


@detect.command('disable-test')
@click.argument('test')
@click.option('-t', '--tags', help='only disable for these tags (comma-separated list)', type=str, default='')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def disable_test(controller, test, tags):
    """ Remove test from your queue """
    with Spinner():
        controller.disable_test(ident=test, tags=tags)


@detect.command('social-stats')
@click.argument('test')
@click.option('-d', '--days', help='days to look back', default=30, type=int, show_default=True)
@click.pass_obj
@handle_api_error
def social_statistics(controller, test, days):
    """ Pull social statistics for a specific test """
    with Spinner():
        data = controller.social_stats(ident=test, days=days)
    print_json(data=data)


@detect.command('delete-endpoint')
@click.argument('endpoint_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_endpoint(controller, endpoint_id):
    """Delete a probe/endpoint"""
    with Spinner():
        controller.delete_endpoint(ident=endpoint_id)


@detect.command('queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ List all tests in your active queue """
    with Spinner():
        iam = IAMController(account=controller.account)
        queue = iam.get_account().get('queue')
        print_json(data=queue)


@detect.command('endpoints')
@click.option('-d', '--days', help='only show endpoints that have run at least once in the past DAYS days', default=90, type=int)
@click.pass_obj
@handle_api_error
def endpoints(controller, days):
    """ List all active endpoints associated to your account """
    with Spinner():
        data = controller.list_endpoints(days=days)
    print_json(data=data)


@detect.command('advisories')
@click.pass_obj
@click.option('-y', '--year', help='View advisories from a specific year', default=None, type=int)
@handle_api_error
def advisories(controller, year):
    """ List all Prelude advisories """
    with Spinner():
        print_json(data=controller.list_advisories(year=year))


@detect.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Download all tests to your local environment """
    
    async def fetch(test):
        click.secho(f'Cloning {test["id"]}')
        Path(test['id']).mkdir(parents=True, exist_ok=True)

        for attach in controller.get_test(test_id=test['id']).get('attachments'):
            if Path(attach).suffix:
                code = controller.download(test_id=test['id'], filename=attach)
                with open(PurePath(test['id'], attach), 'wb') as f:
                    f.write(code)

    async def start_cloning():
        await asyncio.gather(*[fetch(test) for test in controller.list_tests()])

    with Spinner():
        asyncio.run(start_cloning())
        click.secho('Project cloned successfully', fg='green')


@detect.command('activity')
@click.option('-v', '--view',
              help='retrieve a specific result view',
              default='logs', show_default=True,
              type=click.Choice(['logs', 'days', 'insights', 'probes', 'advisories', 'tests']))
@click.option('-d', '--days', help='days to look back', default=30, type=int)
@click.option('--tests', help='comma-separated list of test IDs', type=str)
@click.option('--tags', help='comma-separated list of tags', type=str)
@click.option('--endpoints', help='comma-separated list of endpoint IDs', type=str)
@click.option('--dos', help='comma-separated list of DOS', type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days, view, tests, tags, endpoints, dos):
    """ View my Detect results """
    filters = dict(
        start=datetime.utcnow() - timedelta(days=days),
        finish=datetime.utcnow() + timedelta(days=1)
    )
    if tests:
        filters['tests'] = tests
    if tags:
        filters['tags'] = tags
    if endpoints:
        filters['endpoints'] = endpoints
    if dos:
        filters['dos'] = dos

    with Spinner():
        data = controller.describe_activity(view=view, filters=filters)
    print_json(data=data)
