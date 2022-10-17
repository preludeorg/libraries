import click
from rich import print_json

from detect_sdk.models.codes import Colors, RunCode
from detect_cli.views.shared import handle_api_error
from detect_sdk.controllers.detect_controller import DetectController


@click.group()
@click.pass_context
def detect(ctx):
    """ Continuously test your endpoints """
    ctx.obj = DetectController(account=ctx.obj)


@detect.command('register')
@click.option('--tag', help='add a custom tag to this endpoint')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tag):
    """Register a new endpoint"""
    endpoint_token = controller.register_endpoint(name=name, tag=tag)
    click.secho('Endpoint token: %s' % endpoint_token, fg=Colors.GREEN.value)


@detect.command('activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.argument('endpoint_id')
@click.pass_obj
@handle_api_error
def describe_activity(controller, endpoint_id, days):
    """ Get report for an endpoint """
    activity = controller.describe_activity(days=days, endpoint_id=endpoint_id)
    print_json(data=activity)


@detect.command('activate')
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
    click.secho('Activated %s' % ttp, fg=Colors.GREEN.value)


@detect.command('deactivate')
@click.argument('ttp')
@click.confirmation_option(prompt='Do you want to deactivate the TTP?')
@click.pass_obj
@handle_api_error
def deactivate_ttp(controller, ttp):
    """ Remove TTP from your queue """
    controller.deactivate_ttp(ttp=ttp)
    click.secho('Deactivated %s' % ttp, fg=Colors.GREEN.value)
