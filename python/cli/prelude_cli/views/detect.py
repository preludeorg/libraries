from collections import defaultdict
from datetime import datetime, timedelta, timezone

import click

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import Colors, RunCode, ExitCode

from rich import print_json
from rich.console import Console
from rich.table import Table


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuously test your endpoints """
    ctx.obj = DetectController(account=ctx.obj)


@detect.command('create-endpoint')
@click.option('--tags', help='a comma-separated list of tags for this endpoint', type=str, default='')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tags):
    """ Register a new endpoint """
    endpoint_token = controller.register_endpoint(name=name, tags=tags)
    click.secho(f'Endpoint token: {endpoint_token}', fg=Colors.GREEN.value)


@detect.command('enable-test')
@click.argument('test')
@click.option('--tags', help='only enable for these tags')
@click.option('--run_code',
              help='provide a run_code',
              default='daily', show_default=True,
              type=click.Choice(['daily', 'weekly', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.pass_obj
@handle_api_error
def activate_test(controller, test, run_code, tags):
    """ Add TEST to your queue """
    tags = tags.split(',') if tags else []
    controller.enable_test(ident=test, run_code=RunCode[run_code.upper()].value, tags=tags)


@detect.command('disable-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def deactivate_test(controller, test):
    """ Remove TEST from your queue """
    controller.disable_test(ident=test)
    click.secho(f'Disabled {test}', fg=Colors.GREEN.value)


@detect.command('delete-endpoint')
@click.argument('endpoint_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_endpoint(controller, endpoint_id):
    """Delete a probe/endpoint"""
    controller.delete_endpoint(ident=endpoint_id)
    click.secho(f'Deleted {endpoint_id}', fg=Colors.GREEN.value)


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


@detect.command('probes')
@click.option('--days', help='days to look back', default=7, type=int)
@click.pass_obj
@handle_api_error
def list_probes(controller, days):
    """ List all endpoint probes """
    print_json(data=controller.list_probes(days=days))


@detect.command('activity')
@click.option('--days', help='days to look back', default=30, type=int)
@click.option('--json', '-j', is_flag=True, help='Print data as JSON')
@click.pass_obj
@handle_api_error
def describe_activity(controller, days, json):
    """ View my Detect results """
    start = datetime.now(timezone.utc) - timedelta(days=days)
    finish = datetime.now(timezone.utc)

    raw = controller.describe_activity(start=start, finish=finish)

    if json:
        print_json(data=raw)
    else:
        build = BuildController(account=controller.account)
        tests = {row['id']: row['name'] for row in build.list_tests()}

        report = Table()
        report.add_column('timestamp')
        report.add_column('result ID')
        report.add_column('name')
        report.add_column('test')
        report.add_column('endpoint')
        report.add_column('code', style='magenta')
        report.add_column('status')
        report.add_column('observed')

        for record in raw:
            report.add_row(
                record['date'], 
                record['id'], 
                tests[record['test']], 
                record['test'],
                record['endpoint_id'], 
                str(record['status']),
                ExitCode(record['status']).name,
                'yes' if record.get('observed') else '-'
            )

        console = Console()
        console.print(report)


@detect.command('social-stats')
@click.argument('test')
@click.option('--days', help='days to look back', default=30, type=int)
@click.pass_obj
@handle_api_error
def social_statistics(controller, test, days):
    """ Pull social statistics for a specific test """
    stats = defaultdict(lambda: defaultdict(int))
    for dos, values in controller.stats(ident=test, days=days).items():
        for code, count in values.items():
            stats[dos][ExitCode(int(code)).name] = count
    print_json(data=stats)


@detect.command('observe')
@click.argument('result')
@click.option('--value', help='Mark 1 for observed', default=1, type=int)
@click.pass_obj
@handle_api_error
def observe(controller, result, value):
    """ Mark a result as observed """
    controller.observe(row_id=result, value=value)


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
