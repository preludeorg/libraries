from collections import defaultdict

import click
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import Colors, RunCode
from rich import print_json
from rich.console import Console
from rich.table import Table


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuously test your endpoints """
    ctx.obj = DetectController(account=ctx.obj)


@detect.command('create-endpoint')
@click.option('--tag', help='add a custom tag to this endpoint')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tag):
    """Register a new endpoint"""
    endpoint_token = controller.register_endpoint(name=name, tag=tag)
    click.secho(f'Endpoint token: {endpoint_token}', fg=Colors.GREEN.value)


@detect.command('enable-ttp')
@click.argument('ttp')
@click.option('--run_code',
              help='provide a run-code',
              default='daily',
              type=click.Choice(['daily', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.confirmation_option(prompt='Do you want to activate the TTP?')
@click.pass_obj
@handle_api_error
def activate_ttp(controller, ttp, run_code):
    """ Add TTP to your queue """
    controller.activate_ttp(ttp=ttp, run_code=RunCode[run_code.upper()].value)
    click.secho(f'Activated {ttp}', fg=Colors.GREEN.value)


@detect.command('disable-ttp')
@click.argument('ttp')
@click.confirmation_option(prompt='Do you want to deactivate the TTP?')
@click.pass_obj
@handle_api_error
def deactivate_ttp(controller, ttp):
    """ Remove TTP from your queue """
    controller.deactivate_ttp(ttp=ttp)
    click.secho(f'Deactivated {ttp}', fg=Colors.GREEN.value)


@detect.command('list-queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ View active queue """
    items = controller.print_queue()
    if items:
        print_json(data=items)
    else:
        click.secho('Your queue is empty', fg=Colors.RED.value)


@detect.command('describe-activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days):
    """ View results for my Account """
    days = controller.account_activity(days=days)

    # shape results for overall view
    records = defaultdict(lambda: defaultdict(int))
    for test in days.values():
        for i, tags in test.items():
            for result in tags.values():
                for record in result:
                    records[i]['ok'] += 0
    #print_json(data=records)

    # print to console
    report = Table()
    report.add_column('test')
    report.add_column('tests run')
    report.add_column('total endpoints')
    report.add_column('ok', style='green')
    report.add_column('defended', style='green')
    report.add_column('failed', style='red')
    report.add_column('error', style='magenta')

    for ttp, summary in records.items():
        ok, stopped, failed, error = 0, 0, 0, 0
        volume = sum(summary.values())
        for code, count in summary.items():
            if code == str(103):
                ok = '{0:.0%}'.format(count/volume)
            elif code == str(9):
                stopped = '{0:.0%}'.format(count/volume)
            elif code == str(0):
                failed = '{0:.0%}'.format(count/volume)
            else:
                error = '{0:.0%}'.format(count/volume)
        report.add_row(ttp, str(volume), str(ok), str(stopped), str(failed), str(error))

    console = Console()
    console.print(report)
