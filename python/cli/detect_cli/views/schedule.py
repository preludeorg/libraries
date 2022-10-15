import click

from detect_cli.views.shared import handle_api_error
from detect_sdk.models.codes import RunCode, Colors
from detect_sdk.controllers.schedule_controller import ScheduleController


@click.group()
@click.pass_context
def schedule(ctx):
    """ Schedule TTPs on endpoints """
    ctx.obj = ScheduleController(account=ctx.obj)


@schedule.command('activate-ttp')
@click.argument('ttp_id')
@click.option('--run_code',
              help='provide a run-code',
              default='daily',
              type=click.Choice(['daily', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.confirmation_option(prompt='Do you want to activate the TTP?')
@click.pass_obj
@handle_api_error
def activate_ttp(controller, ttp_id, run_code):
    """Activate a TTP by ID"""
    controller.activate_ttp(ttp=ttp_id, run_code=RunCode[run_code.upper()].value)
    click.secho('Activated %s' % ttp_id, fg=Colors.GREEN.value)


@schedule.command('deactivate-ttp')
@click.argument('ttp_id')
@click.confirmation_option(prompt='Do you want to deactivate the TTP?')
@click.pass_obj
@handle_api_error
def deactivate_ttp(controller, ttp_id):
    """Deactivate a TTP by ID"""
    controller.deactivate_ttp(ttp=ttp_id)
    click.secho('Deactivated %s' % ttp_id, fg=Colors.GREEN.value)
