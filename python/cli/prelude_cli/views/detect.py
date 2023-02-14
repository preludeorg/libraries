import click

from datetime import datetime, timedelta, timezone
from rich import print_json
from rich.console import Console
from rich.table import Table
from collections import defaultdict

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import RunCode, ExitCode, ExitCodeGroup


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuously test your endpoints """
    ctx.obj = DetectController(account=ctx.obj)


@detect.command('create-endpoint')
@click.option('-t', '--tags', help='a comma-separated list of tags for this endpoint', type=str, default='')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tags):
    """ Register a new endpoint """
    token = controller.register_endpoint(name=name, tags=tags)
    click.secho(f'Your token: {token}', fg='green')


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
    """ Add TEST to your queue """
    controller.enable_test(ident=test, run_code=RunCode[run_code.upper()].value, tags=tags)


@detect.command('disable-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def deactivate_test(controller, test):
    """ Remove TEST from your queue """
    controller.disable_test(ident=test)
    click.secho(f'Disabled {test}', fg='green')


@detect.command('delete-endpoint')
@click.argument('endpoint_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_endpoint(controller, endpoint_id):
    """Delete a probe/endpoint"""
    controller.delete_endpoint(ident=endpoint_id)
    click.secho(f'Deleted {endpoint_id}', fg='green')


@detect.command('queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ List all tests in your active queue """
    build = BuildController(account=controller.account)
    tests = {row['id']: row['name'] for row in build.list_tests()}
    active = controller.print_queue()
    for q in active:
        q['run_code'] = RunCode(q['run_code']).name
        q['name'] = tests[q['test']]
    print_json(data=active)


@detect.command('search')
@click.argument('cve')
@click.pass_obj
@handle_api_error
def search(controller, cve):
    """ Search the NVD for a specific CVE identifier """
    print("This product uses the NVD API but is not endorsed or certified by the NVD.\n")
    print_json(data=controller.search(identifier=cve))


@detect.command('rules')
@click.pass_obj
@handle_api_error
def rules(controller):
    """ Print all Verified Security Rules """
    print_json(data=controller.list_rules())


@detect.command('endpoints')
@click.pass_obj
@click.option('-d', '--days', help='days to look back', default=30, type=int)
@handle_api_error
def endpoints(controller, days):
    """ List all endpoints associated to your account """
    print_json(data=controller.list_endpoints(days=days))


@detect.command('social-stats')
@click.argument('test')
@click.option('-d', '--days', help='days to look back', default=30, type=int)
@click.pass_obj
@handle_api_error
def social_statistics(controller, test, days):
    """ Pull social statistics for a specific test """
    stats = defaultdict(lambda: defaultdict(int))
    for dos, values in controller.social_stats(ident=test, days=days).items():
        for state, count in values.items():
            stats[dos][ExitCode(int(state)).name] = count
    print_json(data=stats)


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
    click.secho('Successfully submitted recommendation', fg='green')


@detect.command('activity')
@click.option('-v', '--view',
              help='retrieve a specific result view',
              default='logs', show_default=True,
              type=click.Choice(['logs', 'days', 'insights', 'probes', 'dos', 'rules']))
@click.option('-d', '--days', help='days to look back', default=7, type=int)
@click.option('--tests', help='comma-separated list of test IDs', type=str)
@click.option('--tags', help='comma-separated list of tags', type=str)
@click.option('--endpoints', help='comma-separated list of endpoint IDs', type=str)
@click.option('--dos', help='comma-separated list of DOS', type=str)
@click.option('--statuses', help='comma-separated list of statuses', type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days, view, tests, tags, endpoints, dos, statuses):
    """ View my Detect results """
    filters = dict(
        start=datetime.now(timezone.utc) - timedelta(days=days),
        finish=datetime.now(timezone.utc)
    )
    if tests:
        filters['tests'] = tests
    if tags:
        filters['tags'] = tags
    if endpoints:
        filters['endpoints'] = endpoints
    if statuses:
        filters['statuses'] = statuses
    if dos:
        filters['dos'] = dos

    raw = controller.describe_activity(view=view, filters=filters)
    report = Table()

    if view == 'logs':
        report.add_column('timestamp')
        report.add_column('test')
        report.add_column('endpoint')
        report.add_column('status')

        raw.reverse()
        for record in raw:
            report.add_row(
                record['date'], 
                record['test'],
                record['endpoint_id'], 
                ExitCode(record['status']).name
            )

    elif view == 'insights':
        report.add_column('dos')
        report.add_column('test')
        report.add_column('tag')
        report.add_column('protected', style='green')
        report.add_column('unprotected',  style='red')
        report.add_column('error', style='yellow')
    
        for ins in raw:
            vol = ins['volume']
            report.add_row(
                ins['dos'], 
                ins['test'], 
                ins['tag'], 
                str(vol["protected"]),
                str(vol["unprotected"]),
                str(vol["error"])
            )

    elif view == 'probes':
        report.add_column('endpoint_id')
        for endpoint_id in raw:
            report.add_row(endpoint_id)

    elif view == 'days':
        report.add_column('date')
        report.add_column('protected', style='green')
        report.add_column('unprotected',  style='red')
        report.add_column('error', style='yellow')

        for date, states in raw.items():
            report.add_row(
                date, 
                str(states.get(ExitCodeGroup.PROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.UNPROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.ERROR.name, 0)), 
            )

    elif view == 'dos':
        report.add_column('dos')
        report.add_column('protected', style='green')
        report.add_column('unprotected',  style='red')
        report.add_column('error', style='yellow')

        for dos, states in raw.items():
            report.add_row(
                dos,
                str(states.get(ExitCodeGroup.PROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.UNPROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.ERROR.name, 0)), 
            )

    elif view == 'rules':
        report.add_column('rule')
        report.add_column('protected', style='green')
        report.add_column('unprotected',  style='red')
        report.add_column('error', style='yellow')

        for rule, states in raw.items():
            report.add_row(
                rule,
                str(states.get(ExitCodeGroup.PROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.UNPROTECTED.name, 0)), 
                str(states.get(ExitCodeGroup.ERROR.name, 0)), 
            )

    console = Console()
    console.print(report)
