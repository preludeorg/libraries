import click
from rich import print_json

from detect_cli.views.shared import handle_api_error
from detect_sdk.controllers.manifest_controller import ManifestController


@click.group()
@click.pass_context
def manifest(ctx):
    """ Manage your manifest """
    ctx.obj = ManifestController(account=ctx.obj)


@manifest.command('print')
@click.pass_obj
@handle_api_error
def print_manifest(controller):
    """ View TTP manifest """
    print_json(data=controller.print_manifest())
