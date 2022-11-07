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


@detect.command('enable-test')
@click.argument('test')
@click.option('--tags', help='only enable for these tags')
@click.option('--run_code',
              help='provide a run_code',
              default='daily',
              type=click.Choice(['daily', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.pass_obj
@handle_api_error
def activate_test(controller, test, run_code, tags):
    """ Add test to your queue """
    tags = tags.split(',') if tags else []
    controller.enable_test(ident=test, run_code=RunCode[run_code.upper()].value, tags=tags)


@detect.command('disable-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def deactivate_test(controller, test):
    """ Remove test from your queue """
    controller.disable_test(ident=test)
    click.secho(f'Disabled {test}', fg=Colors.GREEN.value)


@detect.command('list-queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ View active queue """
    print_json(data=controller.print_queue())


@detect.command('describe-activity')
@click.option('--days', help='days to look back', default=7, type=int)
@click.option('--test', help='retrieve detailed data for a single test', type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days, test):
    """ View report for my Account """
    if test:
        raw = controller.describe_activity(days=days, ident=test)
        print_json(data=raw)
    else:
        raw = controller.describe_activity(days=days)

        report = Table()
        report.add_column('test')
        report.add_column('endpoints (#)')
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


@detect.command('list-tags')
@click.pass_obj
@handle_api_error
def list_tags(controller):
    """ List all endpoint tags """
    print_json(data=controller.list_tags())
