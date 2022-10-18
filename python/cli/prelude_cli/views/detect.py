import click
from rich import print_json

from prelude_sdk.models.codes import Colors, RunCode
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.detect_controller import DetectController


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


@detect.command('describe-activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.option('--endpoint_id', help='filter to a specific endpoint', default=None, type=str)
@click.pass_obj
@handle_api_error
def describe_activity(controller, endpoint_id, days):
    """ View results for my Account """
    if endpoint_id:
        print_json(data=controller.endpoint_activity(days=days, endpoint_id=endpoint_id))
    else:
        print_json(data=controller.account_activity(days=days))


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
