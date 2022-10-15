import click
from detect_cli.views.shared import handle_api_error
from rich import print_json

from detect_sdk.controllers.operator_controller import OperatorController


@click.group()
@click.pass_context
def operator(ctx):
    """ Interact with TTP manifest """
    ctx.obj = OperatorController(account=ctx.obj)


@operator.command('manifest')
@click.pass_obj
@handle_api_error
def manifest(controller):
    """ Print Account manifest """
    print_json(data=controller.print_manifest())
