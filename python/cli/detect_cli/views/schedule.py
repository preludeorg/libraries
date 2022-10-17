import click

from detect_cli.views.shared import handle_api_error
from detect_sdk.models.codes import RunCode, Colors
from detect_sdk.controllers.schedule_controller import ScheduleController


@click.group()
@click.pass_context
def schedule(ctx):
    """ Send TTPs to endpoints """
    ctx.obj = ScheduleController(account=ctx.obj)


@schedule.command('activate')
@click.argument('ttp')
@click.option('--run_code',
              help='provide a run-code',
              default='daily',
              type=click.Choice(['daily', 'monthly', 'once', 'debug'], case_sensitive=False))
@click.confirmation_option(prompt='Do you want to activate the TTP?')
@click.pass_obj
@handle_api_error
def activate_ttp(controller, ttp, run_code):
    """ Add TTP to active queue """
    controller.activate_ttp(ttp=ttp, run_code=RunCode[run_code.upper()].value)
    click.secho('Activated %s' % ttp, fg=Colors.GREEN.value)


@schedule.command('deactivate')
@click.argument('ttp')
@click.confirmation_option(prompt='Do you want to deactivate the TTP?')
@click.pass_obj
@handle_api_error
def deactivate_ttp(controller, ttp):
    """ Remove TTP from active queue """
    controller.deactivate_ttp(ttp=ttp)
    click.secho('Deactivated %s' % ttp, fg=Colors.GREEN.value)
