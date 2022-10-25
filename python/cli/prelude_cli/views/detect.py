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
@click.option('--days', help='days to look back', default=7, type=int)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days):
    """ View report for my Account """
    raw = controller.describe_activity(days=days)

    report = Table()
    report.add_column('test')
    report.add_column('volume (#)')
    report.add_column('ok (%)', style='green')
    report.add_column('defended (%)', style='green')
    report.add_column('failed (%)', style='red')
    report.add_column('error (%)', style='magenta')

    for i, test in raw.items():
        ok = test.get('OK', 0)
        stopped = test.get('DETECTED', 0)
        failed = test.get('FAILED', 0)
        error = test.get('ERROR', 0)
        volume = ok + stopped + failed + error
        report.add_row(i, str(volume), str(round((ok / volume) * 100)), str(round((stopped / volume) * 100)),
                       str(round((failed / volume) * 100)), str(round((error / volume) * 100)))

    console = Console()
    console.print(report)


@detect.command('export-report')
@click.option('--days', help='days to look back', default=7, type=int)
@click.pass_obj
@handle_api_error
def export_report(controller, days):
    """ Review all failed tests """
    url = controller.export_report(days=days)
    print(url)
    click.secho(f'Use the above URL to download data dump', fg=Colors.GREEN.value)
