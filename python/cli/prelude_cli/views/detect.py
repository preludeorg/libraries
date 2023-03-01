import click

from rich import print_json
from datetime import datetime, timedelta, time

from prelude_sdk.models.codes import RunCode
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.detect_controller import DetectController


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuous security testing """
    ctx.obj = DetectController(**ctx.obj)


@detect.command('create-endpoint')
@click.option('-t', '--tags', help='a comma-separated list of tags for this endpoint', type=str, default='')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tags):
    """ Register a new endpoint """
    token = controller.register_endpoint(name=name, tags=tags)
    click.secho(token)


@detect.command('tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ List all security tests """
    print_json(data=controller.list_tests())


@detect.command('enable-test')
@click.argument('test')
@click.option('-t', '--tags', help='only enable for these tags (comma-separated list)', type=str, default='')
@click.option('-r', '--run_code',
              help='provide a run_code',
              default='daily', show_default=True,
              type=click.Choice(['daily', 'weekly', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.pass_obj
@handle_api_error
def activate_test(controller, test, run_code, tags):
    """ Add test to your queue """
    controller.enable_test(ident=test, run_code=RunCode[run_code.upper()].value, tags=tags)


@detect.command('disable-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def deactivate_test(controller, test):
    """ Remove test from your queue """
    controller.disable_test(ident=test)


@detect.command('delete-endpoint')
@click.argument('endpoint_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_endpoint(controller, endpoint_id):
    """Delete a probe/endpoint"""
    controller.delete_endpoint(ident=endpoint_id)


@detect.command('queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ List all tests in your active queue """
    print_json(data=controller.list_queue())


@detect.command('search')
@click.argument('cve')
@click.pass_obj
@handle_api_error
def search(controller, cve):
    """ Search the NVD for a specific CVE identifier """
    print("This product uses the NVD API but is not endorsed or certified by the NVD.\n")
    print_json(data=controller.search(identifier=cve))


@detect.command('endpoints')
@click.pass_obj
@handle_api_error
def endpoints(controller):
    """ List all endpoints associated to your account """
    print_json(data=controller.list_endpoints())


@detect.command('social-stats')
@click.argument('test')
@click.option('-d', '--days', help='days to look back', default=30, type=int)
@click.pass_obj
@handle_api_error
def social_statistics(controller, test, days):
    """ Pull social statistics for a specific test """
    print_json(data=controller.social_stats(ident=test, days=days))


@detect.command('recommendations')
@click.pass_obj
@handle_api_error
def recommendation(controller):
    """ Print all security recommendations """
    print_json(data=controller.recommendations())


@detect.command('add-recommendation')
@click.argument('title')
@click.argument('description')
@click.pass_obj
@handle_api_error
def add_recommendation(controller, title, description):
    """ Create a new security recommendation """
    controller.create_recommendation(title=title, description=description)


@detect.command('activity')
@click.option('-v', '--view',
              help='retrieve a specific result view',
              default='logs', show_default=True,
              type=click.Choice(['logs', 'days', 'insights', 'probes', 'rules']))
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
        start=datetime.combine(datetime.utcnow() - timedelta(days=days), time.min),
        finish=datetime.combine(datetime.utcnow(), time.max)
    )
    if tests:
        filters['tests'] = tests
    if tags:
        filters['tags'] = tags
    if endpoints:
        filters['endpoints'] = endpoints
    if dos:
        filters['dos'] = dos

    print_json(data=controller.describe_activity(view=view, filters=filters))
    