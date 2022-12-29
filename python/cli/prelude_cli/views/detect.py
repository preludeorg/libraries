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
@click.option('--tags', help='a comma-separated list of tags for this endpoint', default='', type=str)
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tags=''):
    """ Register a new endpoint """
    endpoint_token = controller.register_endpoint(name=name, tags=tags.split(','))
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


@detect.command('list-queue')
@click.pass_obj
@handle_api_error
def queue(controller):
    """ List all tests in your active queue """
    print_json(data=controller.print_queue())


@detect.command('list-probes')
@click.pass_obj
@handle_api_error
def list_probes(controller):
    """ List all endpoint probes """
    print_json(data=controller.list_probes())


@detect.command('activity')
@click.option('--days', help='days to look back', default=7, type=int)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days):
    """ View my Detect results """
    raw = controller.describe_activity(days=days)

    report = Table()
    report.add_column('date')
    report.add_column('test')
    report.add_column('endpoint')
    report.add_column('status', style='magenta')

    for record in raw:
        report.add_row(record['date'], record['test'], record['endpoint_id'], str(record['status']))

    console = Console()
    console.print(report)
